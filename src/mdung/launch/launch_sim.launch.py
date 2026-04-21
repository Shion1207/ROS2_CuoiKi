from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    package_share = get_package_share_directory("mdung")
    gazebo_launch = os.path.join(package_share, "launch", "gazebo.launch.py")
    gazebo_rviz = os.path.join(package_share, "rviz", "gazebo_display.rviz")
    enable_drive = LaunchConfiguration("enable_drive")

    return LaunchDescription(
        [
            DeclareLaunchArgument("enable_drive", default_value="false"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(gazebo_launch),
                launch_arguments={"enable_drive": enable_drive}.items(),
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", gazebo_rviz],
            ),
            Node(
                package="mdung",
                executable="arm_cmd_to_trajectory.py",
                name="arm_cmd_to_trajectory",
                output="screen",
            ),
        ]
    )
