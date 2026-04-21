#!/usr/bin/env python3

import rclpy
from gazebo_msgs.srv import SetModelConfiguration
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class ArmCmdToTrajectory(Node):
    def __init__(self) -> None:
        super().__init__("arm_cmd_to_trajectory")
        self.declare_parameter("model_name", "mdung")
        self.declare_parameter("link1_min", -1.57)
        self.declare_parameter("link1_max", 1.57)
        self.declare_parameter("link2_min", 0.0)
        self.declare_parameter("link2_max", 0.15)
        self.declare_parameter("default_duration", 1.0)

        self.link1_min = float(self.get_parameter("link1_min").value)
        self.link1_max = float(self.get_parameter("link1_max").value)
        self.link2_min = float(self.get_parameter("link2_min").value)
        self.link2_max = float(self.get_parameter("link2_max").value)
        self.default_duration = float(self.get_parameter("default_duration").value)
        self.model_name = str(self.get_parameter("model_name").value)

        self.subscription = self.create_subscription(
            Float64MultiArray, "arm_cmd", self.arm_cmd_callback, 10
        )
        self.client = self.create_client(
            SetModelConfiguration, "/gazebo/set_model_configuration"
        )

        self.get_logger().info(
            "Waiting for /arm_cmd. Format: [link1_angle, link2_extension, duration_sec(optional)]"
        )
        self.get_logger().info("Waiting for /gazebo/set_model_configuration service...")
        self.client.wait_for_service()
        self.get_logger().info("Connected to Gazebo arm configuration service.")

    def arm_cmd_callback(self, msg: Float64MultiArray) -> None:
        if len(msg.data) < 2:
            self.get_logger().warning(
                "arm_cmd needs at least 2 values: [link1_angle, link2_extension]"
            )
            return

        link1 = max(self.link1_min, min(self.link1_max, float(msg.data[0])))
        link2 = max(self.link2_min, min(self.link2_max, float(msg.data[1])))
        duration = self.default_duration
        if len(msg.data) >= 3:
            duration = max(0.1, float(msg.data[2]))

        request = SetModelConfiguration.Request()
        request.model_name = self.model_name
        request.urdf_param_name = ""
        request.joint_names = ["link1_joint", "link2_joint"]
        request.joint_positions = [link1, link2]

        future = self.client.call_async(request)
        future.add_done_callback(self._handle_response)
        self.get_logger().info(
            f"Commanded arm: link1={link1:.3f}, link2={link2:.3f}, duration={duration:.2f}s"
        )

    def _handle_response(self, future) -> None:
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f"Failed to command arm in Gazebo: {exc}")
            return

        if not response.success:
            self.get_logger().warning(
                f"Gazebo rejected arm command: {response.status_message}"
            )


def main() -> None:
    rclpy.init()
    node = ArmCmdToTrajectory()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
