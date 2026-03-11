# Crazyflies workspace 

This repository contains all ROS 2 packages in the source workspace to run all experiments with [Crazyflies](https://www.bitcraze.io/products/crazyflie-2-1-plus/) that were conducted during my Master's of Applied Sciences degree.

## controller_pkg
This package contains auxiliary nodes to that publish flags that control the experiments, i.e., landing the drones, pausing experiments...

## crazy_encirclement
This package is a private repository containing codes that are still under development as part of my Ph.D. (follow me to see the next updates 👀)

## crazy_encirclement_interfaces
This is also a private repository containing codes that are still under development as part of my Ph.D.

## crazyswarm2
A third-party ROS 2-based stack for Bitcraze Crazyflie multirotor robots.

## lie_group_swarm

This package is decentralized swarm algorithm in which quadcopters are coordinated to follow 3D periodic curves in a collision-free manner, using Lie group operations. For more details, go to the repository to see the documentation, or read the paper published at the IEEE Robotics and Automation Letters: [Decentralized Swarm Control Via SO(3) Embeddings for 3D Trajectories](https://ieeexplore.ieee.org/abstract/document/11260939)

## motion_capture_tracking

This repository is a third-party ROS 2 package that can receive data from various motion capture systems:

- VICON
- Qualisys
- OptiTrack
- VRPN
- NOKOV
- FZMotion
- Motion Analysis

## target_following

This packages is a Reinforcement Larning swarm control for Crazyflies to execute a target following task. The swarm achieves collision-free coordination and cooperation using local observations. For more details, go to the repository to see the documentation, or read the paper published at the IEEE Systems Conference: [Scalable Swarm Control Using Deep Reinforcement Learning](https://ieeexplore.ieee.org/abstract/document/11014655)

