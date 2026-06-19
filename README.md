# A Low-Cost Miniature Mobile Robotic Platform for Education

# A Low-Cost Miniature Mobile Robotic Platform for Education and Swarm Robotics Experiments

## Overview

This repository presents a low-cost miniature mobile robotic platform developed for educational purposes and swarm robotics research.

The platform was designed to provide an affordable, scalable, and reproducible solution for teaching and experimentation in:

* Swarm Robotics
* Mobile Robotics
* Embedded Systems
* Autonomous Navigation
* Multi-Agent Systems
* STEM Education

The project was developed as part of the Master's Degree in Applied Computer Science at the State University of Santa Catarina (UDESC), Brazil.

---

## Features

* Low-cost hardware architecture
* ESP32-based control system
* Wi-Fi and Bluetooth communication
* Differential-drive locomotion
* Infrared obstacle detection
* 3D-printed chassis
* Modular electronic design
* Multi-robot experimentation support
* Educational robotics applications

---

## Robot Architecture

### Hardware Components

| Component               | Description                 |
| ----------------------- | --------------------------- |
| ESP32-WROVER            | Main microcontroller        |
| MPU6050                 | Accelerometer and gyroscope |
| L293D                   | Motor driver                |
| PCF8574                 | I/O expansion               |
| Infrared Sensors        | Obstacle detection          |
| Stepper Motors 28BYJ-48 | Locomotion                  |
| Li-Ion Battery          | Power supply                |

---

## Mechanical Design

The robot structure was designed using CAD software and manufactured using FDM 3D printing technology with PLA filament.

Main components:

* Main chassis
* Wheel assemblies
* Battery enclosure
* Controller support structure

---

## Communication System

The platform supports:

* Wi-Fi communication
* Bluetooth communication
* REST API interface
* UDP robot discovery mechanism

This architecture enables scalable multi-robot deployments and remote monitoring.

---

## Research Applications

The platform can be used in studies involving:

* Swarm Intelligence
* Collective Behaviour
* Formation Control
* Obstacle Avoidance
* Distributed Decision Making
* Robot Coordination
* Autonomous Navigation

---

## Repository Structure

```text
/
├── firmware/
├── cad/
├── pcb/
├── documentation/
├── images/
├── videos/
├── experiments/
└── paper/
```

---

## Publication

### A Low-Cost Miniature Mobile Robotic Platform for Education and Swarm Robotics Experiments

Authors:

* Laurindo Vilonga Dumba
* Yuri Kaszubowski Lopes
* Miraceli Bonjardim Waldemar
* Luciano Abreu Wayand

Abstract:

This work presents a low-cost robotic platform designed for education and swarm robotics research. The platform combines wireless communication, onboard sensing, modular electronics, and a 3D-printable chassis to provide an accessible framework for experimentation in collective robotics.

---

## Future Work

Planned developments include:

* ROS2 integration
* SLAM implementation
* Multi-agent coordination algorithms
* Reinforcement Learning
* Computer Vision modules
* Swarm behaviour experiments

---

## Demonstration

Add photos, videos, and experimental results here.

Example:

![Robot Prototype](images/robot.jpg)

---

## Citation

If you use this platform in your research, please cite:

```bibtex
@article{dumba2026swarmrobotics,
  title={A Low-Cost Miniature Mobile Robotic Platform for Education and Swarm Robotics Experiments},
  author={Dumba, Laurindo Vilonga and Lopes, Yuri Kaszubowski and Waldemar, Miraceli Bonjardim and Wayand, Luciano Abreu},
  year={2026}
}
```

---

## Contact

Laurindo Vilonga Dumba

M.Sc. Candidate in Applied Computer Science

State University of Santa Catarina (UDESC)

Email: [dumbalvd@gmail.com](mailto:dumbalvd@gmail.com)

LinkedIn:
https://www.linkedin.com/in/laurindo-vilonga-dumba-45b214102/
