import rclpy
from rclpy.node import Node

import numpy as np
from enum import IntEnum

from motion_capture_tracking_interfaces.msg import NamedPoseArray
from crazyflie_interfaces.msg import Position


# ===============================
# STATE ENUM
# ===============================
class State(IntEnum):
    IDLE = 0
    TAKEOFF = 1
    HOVER = 2
    ACTIVE = 3
    LAND = 4


# ===============================
# MPME BLACKBOX (placeholder)
# ===============================
class PEGCore:
    def __init__(self, n_pursuers, n_evaders, init_positions):
        pass

    def get_future_position(self, robot, current_position):
        # Replace with real logic
        return current_position


# ===============================
# MAIN NODE
# ===============================
class AsifMPMENode(Node):

    def __init__(self):
        super().__init__("asif_mpme_node")

        self.info = self.get_logger().info

        # --------------------------
        # PARAMETERS
        # --------------------------
        self.declare_parameter('robots', ['C24', 'C25'])
        self.robots = self.get_parameter('robots').value
        self.n_agents = len(self.robots)

        self.timer_period = 0.1

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
        # TRAJECTORIES
        # --------------------------
        self.init_trajectories()

        # --------------------------
        # GAME
        # --------------------------
        self.initialized = False
        self.init_game()

        # --------------------------
        # TIMER
        # --------------------------
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.info("MPME Node Initialized")

    # =========================================================
    # INITIALIZATION
    # =========================================================
    def init_robot_database(self):

        self.robots_data = {}

        for robot in self.robots:
            self.robots_data[robot] = {
                "initial_pose": np.zeros(3),
                "current_pose": np.zeros(3),

                "has_initial_pose": False,

                "state": State.IDLE,
                "hover_height": 0.5,

                "takeoff_index": 0,

                # references
                "takeoff_start_pose": None,

                # assignment
                "role": None,
                "active": False,
                "assigned_target": None,
            }

    def init_publishers(self):

        self.position_pub = {}

        for robot in self.robots:
            self.position_pub[robot] = self.create_publisher(
                Position, f'/{robot}/cmd_position', 10
            )

    def init_subscribers(self):

        self.create_subscription(
            NamedPoseArray,
            "/poses",
            self.pose_callback,
            10
        )

    def init_trajectories(self):

        self.tTO_max = 3.0
        self.t_takeoff = np.arange(
            0, self.tTO_max, self.timer_period
        )

    def init_game(self):

        self.no_pursuers = 2
        self.no_evaders = max(0, self.n_agents - self.no_pursuers)

        self.peg = None

    # =========================================================
    # CALLBACKS
    # =========================================================
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
                self.info(f"{robot} initial pose set")

            # Always update current pose
            data["current_pose"] = pos

        # Initialize game once
        if not self.initialized and self.all_initial_received():
            self.initialize_game()

    # =========================================================
    # GAME INIT
    # =========================================================
    def all_initial_received(self):
        return all(
            data["has_initial_pose"]
            for data in self.robots_data.values()
        )

    def initialize_game(self):

        self.info("Initializing MPME Game")

        init_positions = np.array([
            self.robots_data[r]["initial_pose"][:2]
            for r in self.robots
        ])

        self.peg = PEGCore(
            self.no_pursuers,
            self.no_evaders,
            init_positions
        )

        # Example roles (replace with your logic)
        for i, robot in enumerate(self.robots):
            data = self.robots_data[robot]

            if i < self.no_pursuers:
                data["role"] = "pursuer"
            else:
                data["role"] = "evader"
                data["active"] = True  # example

        self.initialized = True

    # =========================================================
    # TIMER LOOP (CORE LOGIC)
    # =========================================================
    def timer_callback(self):

        if not self.initialized:
            return

        self.update_assignments()

        for robot in self.robots:

            data = self.robots_data[robot]

            if not data["has_initial_pose"]:
                continue

            # --------------------------
            # IDLE → TAKEOFF trigger
            # --------------------------
            eligible = (
                (data["role"] == "evader" and data["active"]) or
                (data["role"] == "pursuer" and data["assigned_target"] is not None)
            )

            if eligible and data["state"] == State.IDLE:
                data["state"] = State.TAKEOFF
                data["takeoff_index"] = 0
                data["takeoff_start_pose"] = data["current_pose"].copy()
                self.info(f"{robot} → TAKEOFF")

            # --------------------------
            # STATE MACHINE
            # --------------------------
            if data["state"] == State.TAKEOFF:
                self.handle_takeoff(robot)

            elif data["state"] == State.HOVER:
                self.handle_hover(robot)

            elif data["state"] == State.ACTIVE:
                self.handle_active(robot)

    # =========================================================
    # STATE HANDLERS
    # =========================================================
    def handle_takeoff(self, robot):

        data = self.robots_data[robot]
        i = data["takeoff_index"]

        r_des = self.takeoff_position(robot, i)
        self.send_position(robot, r_des)

        if i < len(self.t_takeoff) - 1:
            data["takeoff_index"] += 1
        else:
            data["state"] = State.HOVER
            self.info(f"{robot} → HOVER")

    def handle_hover(self, robot):

        data = self.robots_data[robot]

        r_des = self.hover_position(robot)
        self.send_position(robot, r_des)

        if data["assigned_target"] is not None:
            data["state"] = State.ACTIVE
            self.info(f"{robot} → ACTIVE")

    def handle_active(self, robot):

        data = self.robots_data[robot]

        if data["assigned_target"] is None:
            return

        r_cur = data["current_pose"]

        # MPME BLACKBOX
        r_des = self.peg.get_future_position(robot, r_cur)

        self.send_position(robot, r_des)

    # =========================================================
    # TRAJECTORIES
    # =========================================================
    def takeoff_position(self, robot, i):

        data = self.robots_data[robot]

        p0 = data["takeoff_start_pose"]
        h = data["hover_height"]

        tau = self.t_takeoff[i] / self.t_takeoff[-1]

        z = p0[2] + h * (10*tau**3 - 15*tau**4 + 6*tau**5)

        return np.array([p0[0], p0[1], z])

    def hover_position(self, robot):

        data = self.robots_data[robot]
        p0 = data["takeoff_start_pose"]

        return np.array([p0[0], p0[1], p0[2] + data["hover_height"]])

    # =========================================================
    # CONTROL
    # =========================================================
    def send_position(self, robot, r):

        msg = Position()
        msg.x = float(r[0])
        msg.y = float(r[1])
        msg.z = float(r[2])

        self.position_pub[robot].publish(msg)

    # =========================================================
    # ASSIGNMENT (BLACKBOX HOOK)
    # =========================================================
    def update_assignments(self):

        # Replace with real PEG logic

        for robot in self.robots:
            data = self.robots_data[robot]

            if data["role"] == "pursuer":
                data["assigned_target"] = "some_evader"

    # =========================================================
    # MAIN
    # =========================================================


def main(args=None):
    rclpy.init(args=args)

    node = AsifMPMENode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()