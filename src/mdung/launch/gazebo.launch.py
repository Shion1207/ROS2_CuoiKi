from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os
import xacro


def generate_launch_description():
    package_share = get_package_share_directory("mdung")
    gazebo_share = get_package_share_directory("gazebo_ros")
    package_parent = os.path.dirname(package_share)
    gazebo_models = "/usr/share/gazebo-11/models"
    gazebo_resources = "/usr/share/gazebo-11"

    urdf_path = os.path.join(package_share, "urdf", "mdung.urdf")
    default_world = os.path.join(package_share, "worlds", "mdung_obstacles.world")

    robot_description = xacro.process_file(urdf_path).toxml()

    use_sim_time = LaunchConfiguration("use_sim_time")
    gui = LaunchConfiguration("gui")
    world = LaunchConfiguration("world")
    enable_drive = LaunchConfiguration("enable_drive")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, "launch", "gazebo.launch.py")
        ),
        launch_arguments={
            "world": world,
            "gui": gui,
            "verbose": "true",
        }.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": use_sim_time,
            }
        ],
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity",
            "mdung",
            "-topic",
            "robot_description",
            "-x",
            "0.0",
            "-y",
            "0.0",
            "-z",
            "0.15",
        ],
        output="screen",
    )

    axle_driver = Node(
        package="mdung",
        executable="cmd_vel_to_axle.py",
        name="cmd_vel_to_axle",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(enable_drive),
    )

    encoder_publisher = Node(
        package="mdung",
        executable="encoder_publisher.py",
        name="encoder_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    arm_commander = Node(
        package="mdung",
        executable="arm_cmd_to_trajectory.py",
        name="arm_cmd_to_trajectory",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    joint_state_broadcaster_spawner = ExecuteProcess(
        cmd=[
            "ros2",
            "control",
            "load_controller",
            "--set-state",
            "active",
            "joint_state_broadcaster",
        ],
        output="screen",
    )

    arm_controller_spawner = ExecuteProcess(
        cmd=[
            "ros2",
            "control",
            "load_controller",
            "--set-state",
            "active",
            "arm_controller",
        ],
        output="screen",
    )

    axle_controller_spawner = ExecuteProcess(
        cmd=[
            "ros2",
            "control",
            "load_controller",
            "--set-state",
            "active",
            "axle_controller",
        ],
        output="screen",
        condition=IfCondition(enable_drive),
    )

    spawn_controllers = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    spawn_arm_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[arm_controller_spawner],
        )
    )

    spawn_axle_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=arm_controller_spawner,
            on_exit=[axle_controller_spawner],
        )
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("gui", default_value="true"),
            DeclareLaunchArgument("world", default_value=default_world),
            DeclareLaunchArgument("enable_drive", default_value="false"),
            SetEnvironmentVariable(
                "GAZEBO_MODEL_PATH",
                os.pathsep.join([package_parent, gazebo_models]),
            ),
            SetEnvironmentVariable(
                "GAZEBO_RESOURCE_PATH",
                os.pathsep.join([gazebo_resources, package_share]),
            ),
            SetEnvironmentVariable("GAZEBO_MODEL_DATABASE_URI", ""),
            gazebo,
            robot_state_publisher,
            spawn_entity,
            spawn_controllers,
            spawn_arm_controller,
            spawn_axle_controller,
            axle_driver,
            encoder_publisher,
            arm_commander,
        ]
    )
