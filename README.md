# mdung

`mdung` là tên **package ROS 2**.  
Khi `git clone` repo này về với tên thư mục khác, sau khi build và source thì vẫn chạy bằng:

```bash
ros2 launch mdung gazebo.launch.py
ros2 launch mdung display.launch.py
```


Package ROS 2 mô phỏng robot `car-like` tích hợp:

- tay máy 2 bậc tự do:
  - `link1_joint`: khớp quay
  - `link2_joint`: khớp tịnh tiến
- cảm biến:
  - `LiDAR`
  - `Camera`
  - `Encoder` giả lập từ trạng thái chuyển động

Project dùng `ROS 2 Humble`, `Gazebo Classic` và `RViz2`.

## Chạy nhanh

Nếu đã cài đủ ROS 2 Humble và dependency, người khác clone repo về có thể chạy nhanh theo các lệnh sau:

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
colcon build --packages-select mdung
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
ros2 launch mdung all_demo.launch.py
```

Nếu muốn mở riêng từng phần:

```bash
ros2 launch mdung gazebo.launch.py
ros2 launch mdung display.launch.py
rqt_image_view
ros2 run mdung drive_circle_demo.py
```

## Cấu trúc chính

```bash
src/mdung/
  CMakeLists.txt
  package.xml
  launch/
  meshes/
  rviz/
  scripts/
  urdf/
  worlds/
  config/
```

## Yêu cầu

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic 11

Các package cần thiết thường gồm:

```bash
sudo apt install \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2 \
  ros-humble-rqt-image-view \
  ros-humble-xacro
```

## Build

Từ thư mục gốc workspace:

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
colcon build --packages-select mdung
source install/setup.bash
```

## Thiết lập môi trường

Mỗi terminal mới nên chạy lại:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
```

## Chạy mô phỏng

#### Lệnh chạy tất cả 



### 1. Mở Gazebo

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
ros2 launch mdung gazebo.launch.py
```

### 2. Mở RViz

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
ros2 launch mdung display.launch.py
```

### 3. Mở camera bằng rqt

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
rqt_image_view
```

Sau đó chọn topic ảnh:

```bash
/camera_sensor/image_raw
```

### 4. Chạy demo tổng

Lệnh này sẽ mở Gazebo, RViz, `rqt_image_view` và cho xe chạy demo:

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
ros2 launch mdung all_demo.launch.py
```

## Điều khiển robot

### Cho xe chạy vòng tròn

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
ros2 run mdung drive_circle_demo.py
```

### Điều khiển tay máy tự động

```bash
cd /path/to/repo_root
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=23
export ROS_LOCALHOST_ONLY=1
ros2 run mdung arm_demo_sequence.py
```

## Kiểm tra sensor

### LiDAR

```bash
ros2 topic echo /scan
```

### Camera

```bash
ros2 topic list | grep camera
```

### IMU

```bash
ros2 topic echo /imu
```

### Encoder

```bash
ros2 topic echo /left_encoder_ticks
ros2 topic echo /right_encoder_ticks
ros2 topic echo /left_encoder_distance
ros2 topic echo /right_encoder_distance
ros2 topic echo /left_encoder_velocity
ros2 topic echo /right_encoder_velocity
```
