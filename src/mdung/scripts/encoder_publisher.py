#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
from std_msgs.msg import Float64MultiArray
from std_msgs.msg import Int64
from std_msgs.msg import Int64MultiArray


class EncoderPublisher(Node):
    def __init__(self) -> None:
        super().__init__("encoder_publisher")
        self.declare_parameter("left_joint", "LW_joint")
        self.declare_parameter("right_joint", "RW_joint")
        self.declare_parameter("ticks_per_revolution", 1024)
        self.declare_parameter("wheel_radius", 0.035)
        self.declare_parameter("wheel_base", 0.168)
        self.declare_parameter("publish_rate", 20.0)
        self.declare_parameter("log_rate", 1.0)

        self.left_joint = str(self.get_parameter("left_joint").value)
        self.right_joint = str(self.get_parameter("right_joint").value)
        self.ticks_per_revolution = int(
            self.get_parameter("ticks_per_revolution").value
        )
        self.wheel_radius = float(self.get_parameter("wheel_radius").value)
        self.wheel_base = float(self.get_parameter("wheel_base").value)
        publish_rate = float(self.get_parameter("publish_rate").value)
        log_rate = float(self.get_parameter("log_rate").value)

        self.last_left_ticks = 0
        self.last_right_ticks = 0
        self.left_found = False
        self.right_found = False
        self.have_joint_states = False
        self.linear_cmd = 0.0
        self.angular_cmd = 0.0
        self.left_angle_estimate = 0.0
        self.right_angle_estimate = 0.0
        self.last_update_time = self.get_clock().now()
        self.latest_left_ticks = 0
        self.latest_right_ticks = 0
        self.latest_left_distance = 0.0
        self.latest_right_distance = 0.0
        self.latest_left_velocity = 0.0
        self.latest_right_velocity = 0.0

        self.joint_state_sub = self.create_subscription(
            JointState, "/joint_states", self.joint_state_callback, 20
        )
        self.cmd_vel_sub = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_vel_callback, 20
        )
        self.tick_pub = self.create_publisher(Int64MultiArray, "/encoder_ticks", 20)
        self.left_tick_pub = self.create_publisher(Int64, "/left_encoder_ticks", 20)
        self.right_tick_pub = self.create_publisher(Int64, "/right_encoder_ticks", 20)
        self.distance_pub = self.create_publisher(
            Float64MultiArray, "/encoder_distance", 20
        )
        self.left_distance_pub = self.create_publisher(
            Float64, "/left_encoder_distance", 20
        )
        self.right_distance_pub = self.create_publisher(
            Float64, "/right_encoder_distance", 20
        )
        self.velocity_pub = self.create_publisher(
            Float64MultiArray, "/encoder_velocity", 20
        )
        self.left_velocity_pub = self.create_publisher(
            Float64, "/left_encoder_velocity", 20
        )
        self.right_velocity_pub = self.create_publisher(
            Float64, "/right_encoder_velocity", 20
        )
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_fallback_encoder)
        self.log_timer = self.create_timer(1.0 / log_rate, self.log_encoder_summary)

        self.get_logger().info(
            "Encoder publisher is listening on /joint_states; fallback estimation uses /cmd_vel."
        )

    def angle_to_ticks(self, angle: float) -> int:
        return int(round((angle / (2.0 * math.pi)) * self.ticks_per_revolution))

    def ticks_to_distance(self, ticks: int) -> float:
        revolutions = ticks / float(self.ticks_per_revolution)
        return revolutions * 2.0 * math.pi * self.wheel_radius

    def publish_encoder(
        self, left_ticks: int, right_ticks: int, left_velocity: float, right_velocity: float
    ) -> None:
        left_distance = self.ticks_to_distance(left_ticks)
        right_distance = self.ticks_to_distance(right_ticks)
        left_linear_velocity = left_velocity * self.wheel_radius
        right_linear_velocity = right_velocity * self.wheel_radius

        self.latest_left_ticks = left_ticks
        self.latest_right_ticks = right_ticks
        self.latest_left_distance = left_distance
        self.latest_right_distance = right_distance
        self.latest_left_velocity = left_linear_velocity
        self.latest_right_velocity = right_linear_velocity

        tick_msg = Int64MultiArray()
        tick_msg.data = [left_ticks, right_ticks]
        self.tick_pub.publish(tick_msg)
        self.left_tick_pub.publish(Int64(data=left_ticks))
        self.right_tick_pub.publish(Int64(data=right_ticks))

        distance_msg = Float64MultiArray()
        distance_msg.data = [left_distance, right_distance]
        self.distance_pub.publish(distance_msg)
        self.left_distance_pub.publish(Float64(data=left_distance))
        self.right_distance_pub.publish(Float64(data=right_distance))

        velocity_msg = Float64MultiArray()
        velocity_msg.data = [left_linear_velocity, right_linear_velocity]
        self.velocity_pub.publish(velocity_msg)
        self.left_velocity_pub.publish(Float64(data=left_linear_velocity))
        self.right_velocity_pub.publish(Float64(data=right_linear_velocity))

    def cmd_vel_callback(self, msg: Twist) -> None:
        self.linear_cmd = msg.linear.x
        self.angular_cmd = msg.angular.z

    def joint_state_callback(self, msg: JointState) -> None:
        name_to_index = {name: index for index, name in enumerate(msg.name)}

        if self.left_joint not in name_to_index or self.right_joint not in name_to_index:
            if not (self.left_found and self.right_found):
                self.get_logger().warning(
                    "Waiting for LW_joint and RW_joint in /joint_states."
                )
            return

        self.have_joint_states = True

        left_index = name_to_index[self.left_joint]
        right_index = name_to_index[self.right_joint]

        left_position = msg.position[left_index]
        right_position = msg.position[right_index]
        left_velocity = msg.velocity[left_index] if len(msg.velocity) > left_index else 0.0
        right_velocity = (
            msg.velocity[right_index] if len(msg.velocity) > right_index else 0.0
        )

        left_ticks = self.angle_to_ticks(left_position)
        right_ticks = self.angle_to_ticks(right_position)
        self.publish_encoder(left_ticks, right_ticks, left_velocity, right_velocity)

        self.left_found = True
        self.right_found = True
        self.last_left_ticks = left_ticks
        self.last_right_ticks = right_ticks

    def publish_fallback_encoder(self) -> None:
        if self.have_joint_states:
            return

        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds / 1e9
        if dt <= 0.0:
            return
        self.last_update_time = now

        left_linear = self.linear_cmd - (self.angular_cmd * self.wheel_base / 2.0)
        right_linear = self.linear_cmd + (self.angular_cmd * self.wheel_base / 2.0)

        left_angular = left_linear / self.wheel_radius
        right_angular = right_linear / self.wheel_radius

        self.left_angle_estimate += left_angular * dt
        self.right_angle_estimate += right_angular * dt

        left_ticks = self.angle_to_ticks(self.left_angle_estimate)
        right_ticks = self.angle_to_ticks(self.right_angle_estimate)
        self.publish_encoder(left_ticks, right_ticks, left_angular, right_angular)

    def log_encoder_summary(self) -> None:
        self.get_logger().info(
            "Encoder | "
            f"L ticks={self.latest_left_ticks} dist={self.latest_left_distance:.3f}m vel={self.latest_left_velocity:.3f}m/s | "
            f"R ticks={self.latest_right_ticks} dist={self.latest_right_distance:.3f}m vel={self.latest_right_velocity:.3f}m/s"
        )


def main() -> None:
    rclpy.init()
    node = EncoderPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
