# 🚶 ROS2 Wall-Following Robot

> 📚 **Project from "ROS2 Basics" course - The Construct AI (2026)**

[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue.svg)](https://docs.ros.org/en/humble/)
[![Python](https://img.shields.io/badge/Python-3.10-yellow.svg)](https://www.python.org/)
[![The Construct](https://img.shields.io/badge/The_Construct-AI-orange.svg)](https://www.theconstruct.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Project Overview

Complete ROS2 implementation of an autonomous wall-following robot featuring **Topics**, **Services**, **Actions**, and **Custom Interfaces**. The robot autonomously finds the nearest wall, aligns to it, follows along the wall, and records its odometry path.

**Tested on real hardware** via The Construct AI's Real Robot Lab.

## 🎬 Live Demo - Real Hardware

[![Watch the Demo](https://img.youtube.com/vi/M1bk4puMAvw/maxresdefault.jpg)](https://youtu.be/M1bk4puMAvw)

> 🎥 **[Watch on YouTube](https://youtu.be/M1bk4puMAvw)** - See the robot autonomously find and follow a wall on real hardware via The Construct AI's Real Robot Lab.

**Demonstrates:**
- ✅ Service call (`/find_wall`) for wall alignment
- ✅ Topic-based control loop for wall following
- ✅ Action server (`/record_odom`) recording path
- ✅ Real differential drive mobile robot
- ✅ Live cameras from The Construct lab

## 🌟 Key Features

### 1️⃣ Topics (Pub/Sub Pattern)
- **Subscribes to:** `/scan` (sensor_msgs/LaserScan)
- **Publishes to:** `/cmd_vel` (geometry_msgs/Twist)
- Real-time wall-following control loop
- Distance-based steering decisions

### 2️⃣ Services (Synchronous Request/Response)
- **Service:** `/find_wall` (custom FindWall.srv)
- Robot autonomously finds nearest wall
- Aligns robot perpendicular to wall
- Called BEFORE wall-following starts

### 3️⃣ Actions (Asynchronous with Feedback)
- **Action:** `/record_odom` (custom OdomRecord.action)
- Records (x, y, theta) every second
- Provides distance feedback continuously
- Detects complete lap and returns full path

### 4️⃣ Custom Interfaces
- **FindWall.srv** - Service interface for wall finding
- **OdomRecord.action** - Action interface for odometry recording

## 🏗️ System Architecture

### 3-Node Distributed System

| Node | Role | Subscribes | Publishes | Provides |
|------|------|------------|-----------|----------|
| `wall_following.py` | Main Controller | `/scan` | `/cmd_vel` | - |
| `wall_finder.py` | Service Server | `/scan` | `/cmd_vel` | `/find_wall` |
| `odom_recorder.py` | Action Server | `/odom` | - | `/record_odom` |

### Execution Flow

```
START
  │
  ├─► [1] wall_following.py launches
  │
  ├─► [2] Calls /find_wall service
  │       ↓
  │       wall_finder.py aligns robot to wall
  │       ↓
  │       Returns: success = true
  │
  ├─► [3] Calls /record_odom action
  │       ↓
  │       odom_recorder.py starts recording
  │       (continuous feedback: total distance)
  │
  ├─► [4] Main control loop starts
  │       ↓
  │       Read /scan → Calculate → Publish /cmd_vel
  │       (repeat at 10Hz)
  │
  └─► [5] Action completes on lap detection
          ↓
          Returns: full odometry path
          END
```

## 🎬 Robot Behaviors

### Phase 1: Find Wall (Service Call)
1. Robot uses 360° laser scan to identify closest wall
2. Rotates to face the nearest wall
3. Moves forward until within 0.3m distance
4. Aligns wall to right-hand side

### Phase 2: Follow Wall (Topics)
- **Distance > 0.3m:** Turn right to approach wall
- **Distance < 0.2m:** Turn left to move away
- **0.2m to 0.3m:** Move straight forward
- **Front obstacle < 0.5m:** Sharp left turn (corner detection)

### Phase 3: Record Odometry (Action)
- Records position (x, y, theta) every second
- Continuously reports total distance traveled
- Stops after completing one full lap (within 5cm of start)

## 🤖 Robot Platform

**Hardware:** Real differential drive mobile robot via The Construct AI

**Sensors:**
- 360° LiDAR sensor
- Wheel odometry

**Platform:** The Construct AI Real Robot Lab (cloud-based access)

**Compatibility:** Works with any ROS2 robot publishing:
- `/scan` (sensor_msgs/LaserScan)
- `/odom` (nav_msgs/Odometry)

And subscribing to:
- `/cmd_vel` (geometry_msgs/Twist)

## 📁 Repository Structure

### 📦 wall_follower (Main Package)

| File | Description |
|------|-------------|
| `wall_following.py` | Main controller (subscribes to /scan, publishes to /cmd_vel) |
| `wall_finder.py` | Service server (/find_wall) |
| `odom_recorder.py` | Action server (/record_odom) |
| `main.launch.py` | Launches all 3 nodes together |

### 📦 custom_interfaces (Custom Messages)

| File | Description |
|------|-------------|
| `FindWall.srv` | Service definition for wall finding |
| `OdomRecord.action` | Action definition for odometry recording |

### 🌳 File Tree

```
ros2-wall-following-robot/
│
├── wall_follower/
│   ├── wall_follower/
│   │   ├── __init__.py
│   │   ├── wall_following.py
│   │   ├── wall_finder.py
│   │   └── odom_recorder.py
│   ├── launch/
│   │   ├── main.launch.py
│   │   ├── start_wall_finder.launch.py
│   │   └── start_wall_following.launch.py
│   ├── package.xml
│   ├── setup.py
│   └── setup.cfg
│
└── custom_interfaces/
    ├── srv/
    │   └── FindWall.srv
    ├── action/
    │   └── OdomRecord.action
    ├── CMakeLists.txt
    └── package.xml
```

## 🚀 How to Run

### Prerequisites
- ROS2 Humble (or compatible distribution)
- Python 3.10+
- ROS2-compatible mobile robot or simulation

### Build the Workspace
```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Launch All Nodes Together
```bash
ros2 launch wall_follower main.launch.py
```

### Or Launch Individually
```bash
# Terminal 1: Service server
ros2 launch wall_follower start_wall_finder.launch.py

# Terminal 2: Main wall following
ros2 launch wall_follower start_wall_following.launch.py
```

### Test Service Manually
```bash
ros2 service call /find_wall custom_interfaces/srv/FindWall
```

### Monitor Action
```bash
ros2 action send_goal /record_odom custom_interfaces/action/OdomRecord
```

## 🛠️ Tech Stack

**Framework:** ROS2 Humble  
**Language:** Python

**ROS2 Concepts Demonstrated:**
- Topics (Publishers and Subscribers)
- Services (Synchronous communication)
- Actions (Asynchronous with feedback)
- Custom message interfaces
- Launch files
- Multi-node coordination
- Real hardware deployment

**Testing Platform:** The Construct AI cloud-based Real Robot Lab

## 📊 Implementation Highlights

### Wall-Following Algorithm
```python
if front_distance < 0.5:
    # Corner detected - sharp left turn
    twist.angular.z = HIGH_TURN_SPEED
elif right_distance > 0.3:
    # Too far - approach wall
    twist.angular.z = -TURN_SPEED
elif right_distance < 0.2:
    # Too close - move away
    twist.angular.z = TURN_SPEED
else:
    # Perfect distance - go straight
    twist.angular.z = 0
twist.linear.x = FORWARD_SPEED
```

### Lap Detection
- Records initial position when action starts
- Computes distance from start every second
- Action completes when robot returns within 5cm of start

## 🎓 Learning Outcomes

This project demonstrates proficiency in:
- ✅ All major ROS2 communication patterns
- ✅ Custom interface design (.srv and .action)
- ✅ Multi-node system orchestration
- ✅ Launch file configuration
- ✅ Real-time robot control
- ✅ Sensor data processing (LiDAR + odometry)
- ✅ Autonomous behavior design
- ✅ Real hardware deployment

## 🎓 About

**Author:** Sarath Kumar Komathukattil  
**Course:** ROS2 Basics - The Construct AI (2026)  
**Certification:** ROS2 Basics Certificate

## 🔗 Related Work

🚗 **[Autonomous Vehicle Perception System (Quanser QCar)](https://github.com/SarathKumarKomathukattil/autonomous-vehicle-perception-quanser-qcar)** - End-to-end perception with YOLOv8, ENet, and multi-sensor fusion

🤖 **[7-DOF Robot Motion Planning (CoppeliaSim)](https://github.com/SarathKumarKomathukattil/robot-motion-planning-coppeliasim)** - OMPL motion planning with inverse kinematics

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

---

⭐ **If you find this project interesting, please consider starring the repository!**