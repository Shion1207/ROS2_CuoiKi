#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class ArmDemoSequence(Node):
    def __init__(self) -> None:
        super().__init__("arm_demo_sequence")
        self.publisher = self.create_publisher(Float64MultiArray, "/arm_cmd", 10)

        # Sequence:
        # 1. link1 -> -15 deg
        # 2. link1 -> +15 deg
        # 3. link1 -> 0 deg
        # 4. link2 -> extend
        # 5. link2 -> retract
        self.sequence = [
            ([-math.radians(15.0), 0.0], 1.0, "link1 -> -15 deg"),
            ([math.radians(15.0), 0.0], 1.0, "link1 -> +15 deg"),
            ([0.0, 0.0], 1.0, "link1 -> home"),
            ([0.0, 0.12], 1.0, "link2 -> extend"),
            ([0.0, 0.0], 1.0, "link2 -> retract"),
        ]
        self.index = 0
        self.active_step = None
        self.step_started = None

        # Small startup delay so Gazebo plugin is ready.
        self.start_timer = self.create_timer(1.0, self.start_sequence)
        self.publish_timer = None
        self.get_logger().info("Arm demo sequence will start in 1 second.")

    def start_sequence(self) -> None:
        self.start_timer.cancel()
        self.publish_timer = self.create_timer(0.1, self.step_sequence)

    def step_sequence(self) -> None:
        if self.active_step is None:
            if self.index >= len(self.sequence):
                self.get_logger().info("Arm demo sequence finished.")
                if self.publish_timer is not None:
                    self.publish_timer.cancel()
                return

            self.active_step = self.sequence[self.index]
            self.step_started = self.get_clock().now()
            _, _, label = self.active_step
            self.get_logger().info(f"Starting step {self.index + 1}: {label}")

        positions, duration, label = self.active_step

        cmd = Float64MultiArray()
        cmd.data = [positions[0], positions[1], duration]
        self.publisher.publish(cmd)

        elapsed = (
            self.get_clock().now() - self.step_started
        ).nanoseconds / 1e9
        if elapsed >= duration:
            self.get_logger().info(f"Completed step {self.index + 1}: {label}")
            self.index += 1
            self.active_step = None
            return


def main() -> None:
    rclpy.init()
    node = ArmDemoSequence()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
