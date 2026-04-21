cmake_minimum_required(VERSION 3.8)
project(mdung)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch meshes rviz urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES model.config package.xml
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/cmd_vel_to_axle.py
    scripts/arm_cmd_to_trajectory.py
    scripts/arm_demo_sequence.py
    scripts/drive_circle_demo.py
    scripts/encoder_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
