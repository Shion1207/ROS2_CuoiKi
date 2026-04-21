from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    package_share = get_package_share_directory("mdung")

    gazebo_launch = os.path.join(package_share, "launch", "gazebo.launch.py")
    display_launch = os.path.join(package_share, "launch", "display.launch.py")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={"enable_drive": "true"}.items(),
    )

    display = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(display_launch)
    )

    camera_view = Node(
        package="rqt_image_view",
        executable="rqt_image_view",
        name="rqt_image_view",
        output="screen",
    )

    drive_circle_demo = Node(
        package="mdung",
        executable="drive_circle_demo.py",
        name="drive_circle_demo",
        output="screen",
    )

    return LaunchDescription(
        [
            gazebo,
            TimerAction(period=2.0, actions=[display]),
            TimerAction(period=4.0, actions=[camera_view]),
            TimerAction(period=6.0, actions=[drive_circle_demo]),
        ]
    )
