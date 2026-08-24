---
layout: single
title: "Curriculum Vitae"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
  - /resume/
---

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between; align-items: center; background: var(--global-card-bg-color, #f6f8fa); padding: 12px 18px; border-radius: 8px; border: 1px solid var(--global-border-color, #d0d7de); margin-bottom: 25px;">
  <span style="font-size: 1.05em; font-weight: 600;">
    <i class="fas fa-file-alt icon-pad-right" style="color: #0969da;"></i> Christian Corona &mdash; Resume / CV
  </span>
  <div style="display: flex; gap: 10px; flex-wrap: wrap;">
    <a href="/files/Christian_Corona_Resume.md" class="btn btn--primary" download="Christian_Corona_Resume.md" style="margin: 0; padding: 7px 14px; font-size: 0.88em; border-radius: 6px; text-decoration: none;">
      <i class="fas fa-file-code icon-pad-right"></i> Download Markdown (.md)
    </a>
    
  </div>
</div>

## <i class="fas fa-bullseye icon-pad-right" style="color: #0969da;"></i> Objective

Systems-driven machine learning engineer eager to specialize in robotic control, hardware integration, and perceptive autonomy. Passionate about developing and deploying robust, multi-skill RL policies and state estimation pipelines for platform-agnostic robotic systems including quadrupeds, manipulation platforms, and bipeds.

---

## <i class="fas fa-tools icon-pad-right" style="color: #0969da;"></i> Skills & Technical Stack

* **Robotics & Simulation:** Isaac Lab / Isaac Sim, MuJoCo, ROS 2, LiDAR-Inertial Odometry (LIO), Perceptive Locomotion, Modular Systems
* **Machine Learning & Control:** Deep Reinforcement Learning (DRL), Policy Distillation, Spatio-Temporal Sequence Modeling, Kalman Filtering, PyTorch, JAX, ONNX
* **Programming & Embedded Systems:** C++, C, Python, C#, Real-Time Operating Systems (RTOS), NVIDIA Jetson Deployment, Linux

---

## <i class="fas fa-briefcase icon-pad-right" style="color: #0969da;"></i> Experience

### **IHMC Robotics Lab** (Florida Institute for Human & Machine Cognition)
**AI Engineer Intern – AI Controllers Team** &bull; *Pensacola, FL* &bull; **Summer 2026**  
*Advisor:* Dr. Geoffrey Clark

* **Real-Time C++/ONNX Deployment:** Engineered low-latency C++ deployment pipelines to execute ONNX-exported Deep RL policies directly on NVIDIA Jetson compute modules, transporting motor commands and state feedback over high-frequency Ethernet packets.
* **Multi-Skill RL Policy Design:** Designed end-to-end Reinforcement Learning controllers in Isaac Lab for quadrupedal platforms (specifically Unitree Go2), creating unified multi-skill policies capable of executing running and jumping without discrete mode switching.
  * Formulated command structures inspired by ([arXiv:2602.00678](https://arxiv.org/abs/2602.00678)), establishing nominal running commands and modeling jumping as dynamic offsets driven by a step signal (-1) decaying across takeoff, flight, and post-flight phase-dependent rewards.
  * Structured reward function weights and curriculum learning stages to stabilize multi-terrain agility and dynamic velocity tracking for proprioceptive policies.
* **LiDAR Perceptive Locomotion Architecture (In Progress):** Developing a LiDAR-based perceptive locomotion framework using LIO SLAM to maintain drift-resilient state estimation, terrain awareness, and simple navigation.
  * Adapting the spatio-temporal sequence modeling and teacher-student distillation architecture from REAL ([arXiv:2603.17653](https://arxiv.org/abs/2603.17653v1)) for 3D point cloud LiDAR inputs to build short-term terrain memory and ensure motion consistency under perceptual degradation.
* **Cross-Platform Dynamics:** Focused primary research and hardware deployment on the Unitree Go2 quadruped while acquiring operational knowledge of the kinematics, balance dynamics, and control architectures of IHMC’s in-house bipedal robot.

---

## <i class="fas fa-graduation-cap icon-pad-right" style="color: #0969da;"></i> Education

### **Master of Science in Electrical and Computer Engineering**
**University of Florida**, Gainesville, FL &bull; *August 2026 – May 2028*  
* **Graduate Coursework (Fall 2026):** Stochastic Methods of Engineering (`EEE5544`), Foundations of Digital Signal Processing (`EEE5502`), Fundamentals of Machine Learning (`EEL5840`)

### **Bachelor of Science in Computer Science**, *Magna cum laude*
**Belhaven University**, Jackson, MS &bull; *Graduated April 2026*  
* **Relevant Coursework:** Deep Learning, Differential Equations, Number Theory, Graph Theory

---

## <i class="fas fa-laptop-code icon-pad-right" style="color: #0969da;"></i> Projects

### **Physics-Informed Neural Networks (PINN)** &mdash; *Undergraduate Capstone*
<i class="fab fa-github icon-pad-right"></i> **Repository:** [github.com/chrisrcorona5/Physics-informed-Neural-Network-in-JAX-COVID-SIERD](https://github.com/chrisrcorona5/Physics-informed-Neural-Network-in-JAX-COVID-SIERD)

* Built a JAX-based PINN framework enforcing physical conservation laws to solve complex ODE systems (6-compartment dynamic SEIRD models) with sparse training data under Dr. Jarrod Mau (Belhaven University).

---

## <i class="fas fa-baseball-ball icon-pad-right" style="color: #0969da;"></i> Athletics & Leadership

### **Collegiate Baseball Pitcher**
*Belhaven University / Freed-Hardeman University / Appalachian League*
* Competed in high-level collegiate athletics and the Appalachian MLB-sponsored summer league, developing strong performance under pressure, teamwork, and time-management skills while maintaining high academic honors.

