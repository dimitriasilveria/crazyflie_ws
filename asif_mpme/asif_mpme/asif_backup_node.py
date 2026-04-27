import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy,QoSDurabilityPolicy
from motion_capture_tracking_interfaces.msg import NamedPoseArray
from crazyflie_interfaces.msg import FullState, StringArray, Position
from std_msgs.msg import Bool, Int16, Int16MultiArray
from rclpy.duration import Duration
from std_srvs.srv import Empty
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32MultiArray, Float32
from geometry_msgs.msg import Pose, Twist, PoseStamped
from scipy.linalg import expm, logm
import time
import numpy as np
from typing import Dict, List, Tuple
from crazyflie_py import Crazyswarm
import onnxruntime as ort

# ---------------------------------
# MY STUFFS
#----------------------------------
from asif_mpme.PEG import PEGCore

class AsifMPMENode(Node):
    """
    States:
      0: takeoff trajectory
      1: hover
      2: Policy
      3: landing trajectory
    """

    def __init__(self,swarm=None) -> None:
        super().__init__("asif_mpme_node")
        self.swarm = swarm
        self.info = self.get_logger().info
        self.info("MPME Game Initiated")

        # -----------------------------
        # Parameters
        # -----------------------------
        self.declare_parameter('robots', ['C24', 'C25'])#,'C14','C20']) 
        # self.declare_parameter("robots", ["C20"])  # controlled robots
        self.robots = self.get_parameter('robots').value
        self.n_agents  = len(self.robots)

        self.reboot_client = {}

        for robot in self.robots:
            self.reboot_client[robot] = self.create_client(Empty, 
                                                           robot + '/reboot'
                                                           )

        # Pose storage
        self.has_initial_pose = [False] * self.n_agents
        self.has_final = [False] * self.n_agents
        self.land_flag = [False] * self.n_agents

        self.yaw = 0

        self.final_pose = np.zeros((self.n_agents, 3))
        self.current_pos = np.zeros((self.n_agents, 3))
        self.initial_pose = np.zeros((self.n_agents, 3))

        # self.hover_height = np.array([0.30, 0.30])  #hover heights in m
        self.hover_height = np.full(self.n_agents, 0.30)
        
        self.timer_period = 0.1

        # Takeoff trajectory
        self.i_landing = 0
        self.i_takeoff = 0

        self.tTO_max = 3
        self.t_takeoff = np.arange(0,self.tTO_max,self.timer_period)
        self.r_takeoff = np.zeros((3,len(self.t_takeoff),self.n_agents)) 

        self.tL_max = 3
        self.t_landing = np.arange(self.tL_max, 0.1, -self.timer_period)
        self.r_landing = np.zeros((3,len(self.t_landing),self.n_agents))

        self.position_pub = dict({}) #,'C14':None,'C20':None)
        # self.tactic_pub = dict({}) 
        # self.q_pub = dict({})
        # self.omega_pub = dict({})

        # State machine
        self.state = 0          # 0-take-off, 1-hover, 2-Policy, 3-landing
        
        # self.game_parametrs() Definicao das Variaveis do Daniel
        # My Parameters for MPME Game
        self.no_pursuers = 2
        self.no_evaders = 2
        self.target = [0,0]
        self.initialized = False
        print("Initialization Variable####: ", self.initialized)
        self.peg=None
        self.pursuers_win = False
        self.evaders_win = False
        self.evaders_status = None

        self.evaders = self.robots[self.no_pursuers:]

        self.assignment_pub = self.create_publisher(
                Int16MultiArray, '/assignment', 10
            )
        self.evader_status_pub = self.create_publisher(
                Int16MultiArray, '/evader_status', 10
            )
        self.pursuer_status_pub = self.create_publisher(
                Int16MultiArray, '/pursuer_status', 10
            )

        for i in range(len(self.robots)):
            robot = self.robots[i]
            self.position_pub[robot] = self.create_publisher(Position,'/'+ self.robots[i] + '/cmd_position', 10) #create list with publishers for robot in self.robots


        self.create_subscription(
            Bool,
            '/landing',
            self._landing_callback,
            10)
        self.create_subscription(
            Bool,
            '/encircle',
            self._encircle_callback,
            10)

        qos_profile = QoSProfile(reliability =QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            deadline=Duration(seconds=0, nanoseconds=0))

        self.create_subscription(
            NamedPoseArray, "/poses",
            self._poses_changed, qos_profile
        )

        while (not all(self.has_initial_pose)):
            rclpy.spin_once(self, timeout_sec=0.1)


        for i in range(len(self.robots)):
            robot = self.robots[i]

        if swarm:
            self.timeHelper = self.swarm.timeHelper
            self.allcfs = self.swarm.allcfs

            # arm (one by one)
            for cf in self.allcfs.crazyflies:
                cf.arm(True)
                self.timeHelper.sleep(1.0)

        # input("Press Enter to takeoff")
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.info("MPME Game Initiated")

    # -----------------------------
    # Callbacks
    # -----------------------------
    def timer_callback(self):

        try:
            if self.state == 0:
                if all(self.has_initial_pose):
                    for i,robot in enumerate(self.robots):
                        self.takeoff(robot,i)
                        # self.get_logger().info(f'{robot}, {i}')

            elif self.state == 1:
                for i,robot in enumerate(self.robots):
                    self.hover(robot,i) 
            
            elif self.state == 2:
                if self.pursuers_win or self.evaders_win:
                    print("Game Ended!!!!!!!!!!!!!!!!")
                    for i,robot in enumerate(self.robots):
                        self.land_flag[i]=True
                    # self.state = 3

                # if self.evaders_status is not None:
                #     for id, status in enumerate(self.evaders_status):
                #         print("Evader ", id,": ",status)
                #         if status ==-1:
                #             self.land_flag[self.no_pursuers+id] = True

                print("Initialization Variable######", self.initialized)
                
                # Control_loop_policy returns (x_next, y_next, yaw_next) in meters
                
                
                fut_agent_position, c_a, c_e_s, c_p_s = self.GameLoop()
                self.evaders_status = c_e_s
                self.publish_assignment(c_a)
                self.publish_evader_status(c_e_s)
                self.publish_pursuer_status(c_p_s)
                for i, robot in enumerate(self.robots):
                    print("Future position sending",fut_agent_position[i])
                    
                    # send full [x,y,z] vector
                    self.send_position(fut_agent_position[i], robot)

            elif self.state == 3:
                
                if all(self.has_final):
                    self.get_logger().info(f' landing')
                    for i,robot in enumerate(self.robots):
                        self.landing(robot,i)
                        # self.get_logger().info(f'{robot}, {i}')

                    if self.i_landing < len(self.t_landing)-1:
                        self.i_landing += 1
                    else:
                        if self.swarm:
                            self.allcfs.arm(False)
                            self.timeHelper.sleep(3.0)
                        for i,robot in enumerate(self.robots):
                            self.reboot(robot,i)
                            self.info('Exiting circle node')  
                        self.destroy_node()
                        rclpy.shutdown()  
                else:
                    for i,robot in enumerate(self.robots):
                        self.hover(robot,i)          
        except KeyboardInterrupt:
            self.info('Exiting open loop command node')

    def _poses_changed(self, msg):
        """
        Topic update callback to the motion capture lib's
           poses topic to send through the external position
           to the crazyflie 
        """
        for i,robot in enumerate(self.robots):
            for pose in msg.poses:
                    if pose.name == robot:
                        robot_pose = pose.pose
                        break
            if not self.has_initial_pose[i]:
                self.initial_pose[i, 0] = robot_pose.position.x
                self.initial_pose[i, 1] = robot_pose.position.y
                self.initial_pose[i, 2] = robot_pose.position.z   
                self.initial_phase = np.mod(np.arctan2(self.initial_pose[i, 1], self.initial_pose[i, 0]),2*np.pi)   
                self.takeoff_traj(self.tTO_max,i)
                self.has_initial_pose[i] = True    
                
            elif not self.land_flag[i]:
                self.current_pos[i,0] = robot_pose.position.x
                self.current_pos[i,1] = robot_pose.position.y
                self.current_pos[i,2] = robot_pose.position.z
                # self.yaw = R.from_quat([robot_pose.orientation.x, robot_pose.orientation.y, robot_pose.orientation.z, robot_pose.orientation.w]).as_euler('xyz')[2]

            elif (all(self.has_final) == False) and (self.land_flag[i] == True):
                # self.final_pose = np.zeros(3)
                self.info("Landing...")
                self.final_pose[i,0] = robot_pose.position.x
                self.final_pose[i,1] = robot_pose.position.y
                self.final_pose[i,2] = self.hover_height[i]
                self.landing_traj(self.tL_max,i)
                self.has_final[i] = True
                self.state = 3

    def takeoff(self,robot,i):
        self.send_position(self.r_takeoff[:,self.i_takeoff,i],robot)
        #self.info(f"Publishing to {msg.pose.position.x}, {msg.pose.position.y}, {msg.pose.position.z}")
        if self.i_takeoff < len(self.t_takeoff)-1:
            self.i_takeoff += 1
        else:
            if i == self.n_agents -1:
                self.state = 1

    def takeoff_traj(self,t_max,i):
        # Takeoff trajectory
        # self.t_takeoff = np.arange(0,t_max,self.timer_period)
        self.r_takeoff[0,:,i] = self.initial_pose[i,0]*np.ones(len(self.t_takeoff))
        self.r_takeoff[1,:,i] = self.initial_pose[i,1]*np.ones(len(self.t_takeoff))
        self.r_takeoff[2,:,i] = self.hover_height[i]*(self.t_takeoff/t_max)

    def landing_traj(self,t_max,i):
        # Landing trajectory
        self.i_landing = 0
        self.r_landing[0,:,i] = self.final_pose[i,0]*np.ones(len(self.t_landing))
        self.r_landing[1,:,i] = self.final_pose[i,1]*np.ones(len(self.t_landing))
        self.r_landing[2,:,i] = self.final_pose[i,2]*(self.t_landing/t_max)

    def _landing_callback(self, msg):
        for i in range(self.n_agents):
            self.land_flag[i] = msg.data

        self.state = 3

    def _encircle_callback(self, msg):
        
        self.state = 2

    def hover(self,robot,i):
        hover_pos = np.array([self.initial_pose[i,0],self.initial_pose[i,1],self.hover_height[i]])
        self.send_position(hover_pos,robot)

    def landing(self,robot,i):
        self.send_position(self.r_landing[:,self.i_landing,i],robot)

    def reboot(self,robot,i):
        req = Empty.Request()
        self.reboot_client[robot].call_async(req)
        time.sleep(1.0)    

    def send_position(self,r,robot):

        msg = Position()
        msg.x = float(r[0])
        msg.y = float(r[1])
        msg.z = float(r[2])
        # msg.yaw = float(yaw)

        self.position_pub[robot].publish(msg)

    def interpolate(self, p0, p1, n):
        p0 = np.array(p0)
        p1 = np.array(p1)
        return [tuple(p0 + (p1 - p0) * t) for t in np.linspace(0, 1, n)]
    
################################################################################################
    
    def publish_assignment(self, assignment):
        msg = Int16MultiArray()
        msg.data = np.array(assignment, dtype=np.int16).tolist()

        self.assignment_pub.publish(msg)

    def publish_evader_status(self, evader_status):
        msg = Int16MultiArray()
        msg.data = evader_status.astype(int).tolist()

        self.evader_status_pub.publish(msg)

    def publish_pursuer_status(self, pursuer_status):
        msg = Int16MultiArray()
        msg.data = pursuer_status.astype(int).tolist()

        self.pursuer_status_pub.publish(msg)
    

    def GameLoop(self):
        
        cur_p_pos = self.current_pos[:self.no_pursuers,:]
        cur_e_pos = self.current_pos[self.no_pursuers:
                                       self.no_pursuers+self.no_evaders, :]
        
        # Extract xy positions only
        cur_p_pos_xy = xyz_to_xy(cur_p_pos)
        cur_e_pos_xy = xyz_to_xy(cur_e_pos)

        print("Pursuer Position: ", cur_p_pos_xy)
        print("Evader Position: ", cur_e_pos_xy)


        # Initialize the game if not initialized
        if not self.initialized:
            self.peg = self.make_PEG(cur_p_pos_xy,
                                cur_e_pos_xy, self.target)

            self.initialized = True
            
        # Get future position from the game
        fut_p_xy, fut_e_xy, p_wins, e_wins = self.peg.step(
            cur_p_pos_xy, cur_e_pos_xy, self.target
        )

        fut_xy_pos = np.vstack((
            fut_p_xy, fut_e_xy
        ))

        fut_xyz_pos = xy_to_xyz(fut_xy_pos, 0.3)
        self.pursuers_win = p_wins
        self.evaders_win = e_wins

        print("P_WIN: ", p_wins, " AND E_WIN:", e_wins)

        assignment = self.peg.assignment
        evader_status = self.peg.get_evader_status()
        pursuer_status = self.peg.get_pursuer_status()


        return fut_xyz_pos, assignment, evader_status, pursuer_status

    def make_PEG(self,pursuer, evader, target):
        print("INITIALIZING !!!!!!!!!!!!!!!!")
        peg = PEGCore()
        peg.step(pursuer, evader, target)
        
        return peg


def xyz_to_xy(xyz: np.ndarray) -> np.ndarray:
    """
    Convert (N,3) xyz positions to (N,2) xy positions.

    Parameters
    ----------
    xyz : np.ndarray
        Array of shape (N, 3)

    Returns
    -------
    np.ndarray
        Array of shape (N, 2)
    """
    assert xyz.ndim == 2 and xyz.shape[1] == 3, \
        "Input must have shape (N,3)"

    return xyz[:, :2]

def xy_to_xyz(xy: np.ndarray, z: float = 10.0) -> np.ndarray:
    """
    Convert (N,2) xy positions to (N,3) xyz positions by adding a constant z.

    Parameters
    ----------
    xy : np.ndarray
        Array of shape (N, 2)
    z : float
        Constant z-value to append

    Returns
    -------

    np.ndarray
        Array of shape (N, 3)
    """
    assert xy.ndim == 2 and xy.shape[1] == 2, \
        "Input must have shape (N,2)"

    z_column = np.full((xy.shape[0], 1), z)
    return np.hstack((xy, z_column))


def main() -> None:
    swarm = Crazyswarm()
    if not rclpy.ok():
        rclpy.init()
    node = AsifMPMENode(swarm)
    # node = AsifMPMENode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


