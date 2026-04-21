#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


class CmdVelToAxle(Node):
    def __init__(self) -> None:
        super().__init__("cmd_vel_to_axle")
        self.declare_parameter("wheel_radius", 0.035)
        self.declare_parameter("wheel_base", 0.168)
        self.declare_parameter("max_steer", 0.7)
        self.declare_parameter("publish_rate", 20.0)

        self.wheel_radius = float(self.get_parameter("wheel_radius").value)
        self.wheel_base = float(self.get_parameter("wheel_base").value)
        self.max_steer = float(self.get_parameter("max_steer").value)
        publish_rate = float(self.get_parameter("publish_rate").value)

        self.linear_cmd = 0.0
        self.angular_cmd = 0.0
        self.left_angle = 0.0
        self.right_angle = 0.0
        self.last_time = self.get_clock().now()

        self.subscription = self.create_subscription(
            Twist, "cmd_vel", self.cmd_vel_callback, 10
        )
        self.publisher = self.create_publisher(
            JointTrajectory, "/axle_controller/joint_trajectory", 10
        )
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_joint_targets)

    def cmd_vel_callback(self, msg: Twist) -> None:
        self.linear_cmd = msg.linear.x
        self.angular_cmd = msg.angular.z

    def publish_joint_targets(self) -> None:
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        if dt <= 0.0:
            dt = 1.0 / 20.0
        self.last_time = now

        steer = 0.0
        if abs(self.linear_cmd) > 1e-4 and abs(self.angular_cmd) > 1e-4:
            steer = math.atan(self.wheel_base * self.angular_cmd / self.linear_cmd)
        steer = max(-self.max_steer, min(self.max_steer, steer))

        wheel_speed = self.linear_cmd / self.wheel_radius
        self.left_angle += wheel_speed * dt
        self.right_angle += wheel_speed * dt

        msg = JointTrajectory()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = ""
        msg.joint_names = ["linkage_joint", "LW_joint", "RW_joint"]

        point = JointTrajectoryPoint()
        point.positions = [steer, self.left_angle, self.right_angle]
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = int(0.1 * 1e9)

        msg.points = [point]
        self.publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = CmdVelToAxle()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
