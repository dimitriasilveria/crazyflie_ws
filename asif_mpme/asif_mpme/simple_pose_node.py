import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy,QoSDurabilityPolicy
from geometry_msgs.msg import TransformStamped
from motion_capture_tracking_interfaces.msg import NamedPoseArray

class SimplePoseNode(Node):

    def __init__(self):

        super().__init__('simple_pose_node')

        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription= self.create_subscription(
            NamedPoseArray,
            "/poses", self.pose_callback, qos_profile
        )


    def pose_callback(self,msg):

        print("\n--- New Mocap Frame ---")

        for p in msg.poses:
            name = p.name
            pos = p.pose.position
            ori = p.pose.orientation

            print(f"{name}: "
                  f"pos=({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}) "
                  f"ori=({ori.x:.3f}, {ori.y:.3f}, {ori.z:.3f}, {ori.w:.3f})")

        self.get_logger().info(
            f"{name}_Position: {pos.x:.3f} {pos.y:.3f} {pos.z:.3f}"
        )


def main():

    rclpy.init()

    node = SimplePoseNode()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()