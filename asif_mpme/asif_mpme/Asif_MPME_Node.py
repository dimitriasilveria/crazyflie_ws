import math
from typing import Dict, List, Tuple
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32MultiArray, Float32
from geometry_msgs.msg import Pose, Twist, PoseStamped
from scipy.linalg import expm, logm
from crazyflie_interfaces.msg import FullState, StringArray, Position
import onnxruntime as ort



import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy,QoSDurabilityPolicy
from motion_capture_tracking_interfaces.msg import NamedPoseArray
from std_msgs.msg import Bool, Int16, Int16MultiArray
from rclpy.duration import Duration
from std_srvs.srv import Empty
import time
import numpy as np
from crazyflie_py import Crazyswarm
from crazyflie_interfaces.msg import FullState, StringArray, Position
from enum import IntEnum

# ---------------------------------
# MY STUFFS
#----------------------------------
from asif_mpme.PEG import PEGCore


# ===============================
# STATE ENUM
# ===============================
class State(IntEnum):
    IDLE = 0
    TAKEOFF = 1
    HOVER = 2
    ACTIVE = 3
    LAND = 4

class AsifMPMENode(Node):

    def __init__(self,swarm=None) -> None:
        super().__init__("asif_mpme_node")
        
        self.info = self.get_logger().info
        self.shutdown_requested =  False

        # Initialize Configuration Parameters
        self.swarm = swarm
        self.declare_parameter('robots', ['C24', 'C25'])
        self.robots = self.get_parameter('robots').value
        self.n_agents = len(self.robots)
        
        self.timer_period = 0.1

        self.takeoff_time_max = 3.0
        self.t_takeoff = np.arange(
            0, self.takeoff_time_max, self.timer_period
        )

        self.landing_time_max = 3.0
        self.t_landing = np.arange(
            0, self.landing_time_max, self.timer_period
        )

        # --------------------------
        # DATA STRUCTURE
        # --------------------------
        self.init_robot_database()

        # --------------------------
        # ROS INTERFACES
        # --------------------------
        self.init_publishers()
        self.init_subscribers()

        # --------------------------
        # GAME
        # --------------------------
        self.init_game()
        self.arm_swarm()

        # --------------------------
        # TIMER
        # --------------------------
        self.timer = self.create_timer(self.timer_period, self.timer_callback)


        self.info("AsifMPMENode Initiated")

    def arm_swarm(self, delay=0.5):

        if self.swarm is None:
            self.get_logger().warn("No swarm interface available")
            return

        self.timeHelper = self.swarm.timeHelper
        self.allcfs = self.swarm.allcfs

        self.info("Arming Crazyflies...")

        for cf in self.allcfs.crazyflies:
            try:
                cf.arm(True)
                self.info(f"{cf.prefix} armed")
                self.timeHelper.sleep(delay)
            except Exception as e:
                self.get_logger().error(f"Failed to arm {cf.prefix}: {e}")

    def init_game(self):
        # Game Parameters
        self.no_pursuers = 1
        self.no_evaders = self.no_pursuers
        self.target = np.array([0,0])
        self.initialized = False
        self.pursuers_win = False
        self.evaders_win = False
        self.info("Initializing MPME Game")

    
    def init_robot_database(self):

        self.robots_data = {}

        for robot in self.robots:

            self.robots_data[robot] = {
                "initial_pose": None,
                "current_pose": None,

                "has_initial_pose": False,

                "state": State.IDLE,
                "hover_height": 0.30,

                "takeoff_start_pose":None,
                "takeoff_index": 0,

                "landing_start_pose": None,
                "landing_index":0
            }

    def init_publishers(self):

        self.position_pub = {}

        for robot in self.robots:
            self.position_pub[robot] = self.create_publisher(
                Position, f'/{robot}/cmd_position', 10
            )

    def init_subscribers(self):

        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.create_subscription(
            NamedPoseArray,
            "/poses", self.pose_callback, qos_profile
        )

    
    # =====================================================
    # GAME INIT
    # ====================================================
    def all_initial_received(self):
        return all(
            data["has_initial_pose"]
            for data in self.robots_data.values()
        )
    
    def initialize_game(self):

        initial_positions = []

        for robot in self.robots:

            initial_positions.append(
                self.robots_data[robot]["initial_pose"][:2]
            )

        initial_positions = np.array(initial_positions)

        pursuer_initial_pos = initial_positions[:self.no_pursuers,:]
        evader_initial_pos = initial_positions[self.no_pursuers:
                                               self.no_pursuers+self.no_evaders, :]
        
        self.peg = PEGCore()
        self.peg.game_init(
            pursuer_initial_pos,
            evader_initial_pos,
            self.target
        )
        self.info(str(pursuer_initial_pos))
        self.initialized = True
        self.info("MPME GAME CLASS INITIALIZED")


    # ============================================
    # CALLBACKS
    # ============================================

    def pose_callback(self, msg):

        pose_dict = {p.name: p.pose for p in msg.poses}

        for robot in self.robots:

            if robot not in pose_dict:
                continue

            pose = pose_dict[robot]
            data = self.robots_data[robot]

            pos = np.array([
                pose.position.x,
                pose.position.y,
                pose.position.z
            ])

            # First-time initialization
            if not data["has_initial_pose"]:
                data["initial_pose"] = pos
                data["has_initial_pose"] = True
                self.info(f"{robot} intial pose set")

            # Always update current pose
            data["current_pose"] = pos
            
        # Initialize game once
        if not self.initialized and self.all_initial_received():
            self.initialize_game()

        return None
        
    

    # ====================================================
    # TIMER LOOP (CORE LOGIC)
    # ====================================================

    def timer_callback(self):
        if not self.initialized:
            return
        
        # self.info("Timer loop not yet ready")
        
        
        # If pursuer or Evader wins then:
        # End game
        # Land all the robots
        if self.pursuers_win or self.evaders_win:
            for robot in self.robots:
                data = self.robots_data[robot]
                data["state"] = State.LAND
                self.shutdown_requested = True

        for robot in self.robots:
            data = self.robots_data[robot]
            takeoff_trigger = False
            land_trigger = False
            if data["state"] == State.IDLE:
                self.info(f"{robot} is still IDLE")
                takeoff_trigger =  np.random.choice([True, False])
                # data["state"] = State.TAKEOFF
                # data["takeoff_start_pose"] = data["current_pose"].copy()



            elif data["state"] == State.HOVER:
                self.info(f"{robot} is still in HOVER")
                land_trigger = np.random.choice([True, False])


            if takeoff_trigger:
                data["state"] = State.TAKEOFF
                data["takeoff_start_pose"] = data["current_pose"].copy()
                

            if land_trigger:
                data["state"] = State.LAND
                data["landing_start_pose"] = data["current_pose"].copy()


        

        # Check the robot status
        # How to get robot status from the game
        # If the evaders are active and pursuers are engaged
        # If for those cfs states are IDLE ---> State: Takeoff
        # fut_rob_pos <------ from GameLoop()

        # For each robot

            # if not data["has_intial_pose"]:
            # continue


            # if data["state"] == State.Takeoff:
            # handle takeoff

            # if data["state"] == State.Active()
            # handle_active(): send future position to robots

            # if
        for robot in self.robots:
            
            data = self.robots_data[robot]

            if not data["has_initial_pose"]:
                self.info(f"{robot} is not initialized")
                continue

            if data["state"] == State.IDLE:
                self.info(f"{robot} is in IDLE state")

            elif data["state"] == State.TAKEOFF:
                self.handle_takeoff(robot)

            elif data["state"] == State.LAND:
                self.handle_landing(robot)
                

        if self.shutdown_requested and all(data["state"] == State.IDLE
            for data in self.robots_data.values()):
            self.info("Shutting Down Node")
            self.timer.cancel()
            return
        
        # self.pursuers_win = True 


    def send_position(self, robot, r):

        msg = Position()

        msg.x = float(r[0])
        msg.y = float(r[1])
        msg.z = float(r[2])
        
        self.position_pub[robot].publish(msg)

    def handle_takeoff(self, robot):
        self.info(f"{robot} Taking OFF")
        data = self.robots_data[robot]
        i = data["takeoff_index"]
        des_loc = self.takeoff_position(robot, i)
        self.send_position(robot,des_loc)
        if i < len(self.t_takeoff) -1:
            data["takeoff_index"] += 1
        else:
            data["state"] = State.HOVER
            self.info(f"{robot} → HOVER")

    def takeoff_position(self, robot, i):

        data = self.robots_data[robot]

        p0 = data["takeoff_start_pose"]
        h = data["hover_height"]

        tau = self.t_takeoff[i] / self.t_takeoff[-1]

        z = p0[2] + h * (10*tau**3 - 15*tau**4 + 6*tau**5)

        return np.array([p0[0], p0[1], z])

    

    def handle_landing(self, robot):
        self.info(f"{robot} Landing")
        data = self.robots_data[robot]
        i = data["landing_index"]
        des_loc = self.landing_position(robot,i)
        self.send_position(robot, des_loc)
        if i < len(self.t_landing) - 1:
            data["landing_index"] += 1
        else:
            data["state"] = State.IDLE
            self.info(f"{robot} Landed")

    def landing_position(self, robot, i):

        data = self.robots_data[robot]

        p0 = data["landing_start_pose"]
        z0 = p0[2]

        tau = self.t_landing[i] / self.t_landing[-1]

        s = (10*tau**3 - 15*tau**4 + 6*tau**5)

        z = z0 * (1 - s)   # goes from z0 → 0

        return np.array([p0[0], p0[1], z])




    # def handle_land(self, robot):

    #     data = self.robots_data[robot]
    #     i = data["landing_index"]

    #     p0 = data["current_pose"]
    #     h = p0[2]

    #     tau = (i * self.timer_period) / 3.0
    #     tau = min(tau, 1.0)

    #     z = h * (1 - (10*tau**3 - 15*tau**4 + 6*tau**5))

    #     r_des = np.array([p0[0], p0[1], z])

    #     self.send_position(robot, r_des)

    #     if tau < 1.0:
    #         data["landing_index"] += 1
    #     else:
    #         data["state"] = State.IDLE
    #         self.info(f"{robot} landed")




        


def main() -> None:
    swarm = Crazyswarm()
    if not rclpy.ok():
        rclpy.init()
    node = AsifMPMENode(swarm)
    # node = AsifMPMENode()
    rclpy.spin(node)
    if node.shutdown_requested:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()