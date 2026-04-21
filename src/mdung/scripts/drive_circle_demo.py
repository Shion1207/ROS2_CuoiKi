#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class DriveCircleDemo(Node):
    def __init__(self) -> None:
        super().__init__("drive_circle_demo")
        self.declare_parameter("linear_x", 0.25)
        self.declare_parameter("angular_z", 0.25)
        self.declare_parameter("publish_rate", 10.0)

        self.linear_x = float(self.get_parameter("linear_x").value)
        self.angular_z = float(self.get_parameter("angular_z").value)
        publish_rate = float(self.get_parameter("publish_rate").value)

        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_cmd)
        self.get_logger().info(
            f"Publishing circular cmd_vel: linear.x={self.linear_x:.2f}, angular.z={self.angular_z:.2f}"
        )

    def publish_cmd(self) -> None:
        msg = Twist()
        msg.linear.x = self.linear_x
        msg.angular.z = self.angular_z
        self.publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = DriveCircleDemo()
    try:
        rclpy.spin(node)
    finally:
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
