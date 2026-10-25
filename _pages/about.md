---
permalink: /
title: "Christian Corona"
excerpt: "Machine Learning, Robotics & Control Theory Portfolio"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

<div style="text-align: center; margin-bottom: 25px;">
  <picture>
    <source srcset="/images/humanoids_and_me.webp" type="image/webp">
    <img src="/images/humanoids_and_me.png" alt="Christian Corona with Humanoid Robots" style="max-width: 480px; width: 100%; height: auto; margin: 0 auto; border-radius: 8px; display: block; box-shadow: 0 4px 12px rgba(0,0,0,0.08);" fetchpriority="high" decoding="async">
  </picture>
</div>

# Intro

I am a graduate student at the **University of Florida** in the Electrical and Computer Engineering (ECE) department, specializing in **Machine Learning**, **Robotics**, and **Control Systems**. Previously, I was an AI Intern at the **IHMC Robotics Lab** (Florida Institute for Human and Machine Cognition).

My work bridges learnable control architectures with high-fidelity physics simulators such as NVIDIA Isaac Lab and MuJoCo to deploy robust policies onto physical robots, with a primary focus on zero-shot sim-to-real transfer, perceptive locomotion, and dynamic agility.

---

# Visual Showcase & Simulation Demos

<style>
.recon-video-container {
  position: relative;
  width: 100%;
  margin: 0 auto 10px auto;
}
.recon-video-container #recon-fs-btn {
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease, transform 0.2s ease, background 0.2s ease;
}
.recon-video-container:hover #recon-fs-btn,
.recon-video-container:focus-within #recon-fs-btn {
  opacity: 1;
  pointer-events: auto;
}
</style>

<div style="border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; background: #fafbfc; margin-top: 15px; margin-bottom: 25px;">
  <div class="recon-video-container">
    <video id="recon-video" autoplay loop muted playsinline poster="/images/go2-perceptive-latent-recon.png" style="width: 100%; border-radius: 6px; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
      <source src="/images/go2-perceptive-latent-recon.mp4" type="video/mp4">
      <img src="/images/go2-perceptive-latent-recon.gif" alt="Unitree Go2 Perceptive Sim: Decoder Reconstruction vs Isaac Sim vs MLP/LSTM Latents" style="width: 100%; border-radius: 6px; display: block;">
    </video>
    <button id="recon-fs-btn" onclick="toggleReconFullscreen()" aria-label="Toggle Fullscreen" title="Zoom / Fullscreen Video" style="position: absolute; top: 10px; right: 10px; background: rgba(0, 0, 0, 0.65); color: #fff; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 6px; padding: 6px 12px; font-size: 0.82em; cursor: pointer; display: flex; align-items: center; gap: 6px; backdrop-filter: blur(4px); box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
      <i id="recon-fs-icon" class="fas fa-expand" aria-hidden="true"></i>
      <span id="recon-fs-text">Fullscreen</span>
    </button>
  </div>
  <div style="display: flex; justify-content: space-between; font-size: 0.82em; color: #586069; margin-bottom: 12px; text-align: center; border-bottom: 1px solid #eaecef; padding-bottom: 8px;">
    <span style="flex: 1; padding: 0 5px;"><strong>Left:</strong> Decoder Reconstruction vs Ground Truth</span>
    <span style="flex: 1.4; padding: 0 5px;"><strong>Center:</strong> Unitree Go2 in Isaac Lab (10–14 Hz Spherical LiDAR)</span>
    <span style="flex: 1; padding: 0 5px;"><strong>Right:</strong> MLP & LSTM Latent Feature Activations</span>
  </div>
  <h3 style="margin-top: 0; font-size: 1.15em; text-align: center;">Perceptive Elevation Reconstruction & Latent Neural Representations</h3>
  <p style="font-size: 0.92em; line-height: 1.5; margin-bottom: 0; color: #333; text-align: center; max-width: 820px; margin-left: auto; margin-right: auto;">
    Perception pipeline illustrating how an MLP encoder learns to reconstruct dense ground-truth elevation heightmaps from sparse, asynchronous spherical LiDAR scans (10–14 Hz Unitree L1 4D LiDAR mounted on the Go2 chin). Supervised by auxiliary decoder reconstruction loss, recurrent LSTM temporal memory and MLP latent embeddings capture critical terrain features to empower the Actor policy for robust, extreme terrain navigation.
  </p>
</div>

<script>
function toggleReconFullscreen() {
  var video = document.getElementById('recon-video');
  if (!video) return;
  var isFs = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
  if (!isFs) {
    if (video.requestFullscreen) {
      video.requestFullscreen();
    } else if (video.webkitRequestFullscreen) {
      video.webkitRequestFullscreen();
    } else if (video.mozRequestFullScreen) {
      video.mozRequestFullScreen();
    } else if (video.msRequestFullscreen) {
      video.msRequestFullscreen();
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    }
  }
}

function updateReconFsButton() {
  var icon = document.getElementById('recon-fs-icon');
  var text = document.getElementById('recon-fs-text');
  if (!icon || !text) return;
  var isFs = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
  if (isFs) {
    icon.className = 'fas fa-compress';
    text.textContent = 'Exit Fullscreen';
  } else {
    icon.className = 'fas fa-expand';
    text.textContent = 'Fullscreen';
  }
}

document.addEventListener('fullscreenchange', updateReconFsButton);
document.addEventListener('webkitfullscreenchange', updateReconFsButton);
document.addEventListener('mozfullscreenchange', updateReconFsButton);
document.addEventListener('MSFullscreenChange', updateReconFsButton);
</script>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 15px; margin-bottom: 20px;">

  <div style="border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; background: #fafbfc;">
    <video autoplay loop muted playsinline poster="/images/go2-gap.gif" style="width: 100%; border-radius: 6px; display: block; margin-bottom: 12px;">
      <source src="/images/go2-gap.mp4" type="video/mp4">
      <img src="/images/go2-gap.gif" alt="Perceptive Quadruped Locomotion - Gap Crossing" style="width: 100%; border-radius: 6px; display: block; margin-bottom: 12px;">
    </video>
    <h3 style="margin-top: 0; font-size: 1.1em;">Perceptive Locomotion & Gap Crossing</h3>
    <p style="font-size: 0.92em; line-height: 1.45; margin-bottom: 0; color: #333;">Actor-critic policy with MLP + LSTM latent representation encoding raycaster LiDAR and terrain elevation in NVIDIA Isaac Lab, transferred sim-to-real with Unitree drivers at real-time ROS 2 control frequencies.</p>
  </div>

  <div style="border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; background: #fafbfc;">
    <video autoplay loop muted playsinline poster="/images/go2-stairs.gif" style="width: 100%; border-radius: 6px; display: block; margin-bottom: 12px;">
      <source src="/images/go2-stairs.mp4" type="video/mp4">
      <img src="/images/go2-stairs.gif" alt="Perceptive Quadruped Locomotion - Stairs" style="width: 100%; border-radius: 6px; display: block; margin-bottom: 12px;">
    </video>
    <h3 style="margin-top: 0; font-size: 1.1em;">Perceptive Stair & Extreme Terrain Traversal</h3>
    <p style="font-size: 0.92em; line-height: 1.45; margin-bottom: 0; color: #333;">Latent elevation-conditioned locomotion policy navigating complex stairs, height disparities, and rough obstacles under dynamic physical disturbances.</p>
  </div>

</div>

<div style="border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; background: #fafbfc; margin-bottom: 25px;">
  <video autoplay loop muted playsinline poster="/images/go2-jumping.gif" style="width: 100%; max-width: 580px; border-radius: 6px; display: block; margin: 0 auto 12px auto;">
    <source src="/images/go2-jumping.mp4" type="video/mp4">
    <img src="/images/go2-jumping.gif" alt="Multi-skill Dynamic Locomotion - Jumping" style="width: 100%; max-width: 580px; border-radius: 6px; display: block; margin: 0 auto 12px auto;">
  </video>
  <h3 style="margin-top: 0; font-size: 1.1em; text-align: center;">Multi-Skill Dynamic Locomotion & Jumping</h3>
  <p style="font-size: 0.92em; line-height: 1.45; margin-bottom: 0; color: #333; text-align: center; max-width: 650px; margin-left: auto; margin-right: auto;">Asymmetric actor-critic reinforcement learning policy trained to distinctly modulate between high-speed running gaits and explosive jumping maneuvers within a unified control network.</p>
</div>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 15px; margin-bottom: 20px;">

  <div style="border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; background: #fafbfc;">
    <video autoplay loop muted playsinline preload="none" width="960" height="540" poster="/images/split-belt-reflex.png" aria-label="Planar split-belt treadmill walking with tuned reflex control" style="width: 100%; height: auto; border-radius: 6px; display: block; margin-bottom: 12px;">
      <source src="/images/split-belt-reflex.mp4" type="video/mp4">
      <img src="/images/split-belt-reflex.gif" alt="Planar human model walking on a split-belt treadmill with reflex control tuned using CMA-ES" loading="lazy" decoding="async" width="720" height="405" style="width: 100%; height: auto; border-radius: 6px; display: block; margin-bottom: 12px;">
    </video>
    <h3 style="margin-top: 0; font-size: 1.1em;">Split-Belt Walking &amp; Tuned Reflex Control</h3>
    <p style="font-size: 0.92em; line-height: 1.45; margin-bottom: 0; color: #333;">Planar walking on a split-belt treadmill, with reflex control tuned through CMA-ES optimization. I plan to build on this work to develop exoskeleton control with reinforcement learning.</p>
  </div>

  <div style="border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; background: #fafbfc;">
    <video autoplay loop muted playsinline preload="none" width="960" height="540" poster="/images/musclemimic-amass-walking.png" aria-label="MuscleMimic full-body policy following an AMASS walking clip" style="width: 100%; height: auto; border-radius: 6px; display: block; margin-bottom: 12px;">
      <source src="/images/musclemimic-amass-walking.mp4" type="video/mp4">
      <img src="/images/musclemimic-amass-walking.gif" alt="MuscleMimic full-body human policy following an AMASS walking reference through imitation learning" loading="lazy" decoding="async" width="720" height="405" style="width: 100%; height: auto; border-radius: 6px; display: block; margin-bottom: 12px;">
    </video>
    <h3 style="margin-top: 0; font-size: 1.1em;">MuscleMimic Full-Body Imitation Learning</h3>
    <p style="font-size: 0.92em; line-height: 1.45; margin-bottom: 0; color: #333;">A local evaluation of <a href="https://github.com/amathislab/musclemimic">MuscleMimic</a>'s imitation learning policy following an AMASS walking clip. This full-body setup is part of my planned work on exoskeleton control with reinforcement learning.</p>
  </div>

</div>

---

# Research & Projects

### 1. Robust Perceptive Locomotion in Extreme Terrains (IHMC Robotics Lab)
- **Tech**: NVIDIA Isaac Lab, PyTorch, LiDAR/Heightmap encoder-decoder auxiliary loss, LSTM Policy, ROS 2
- **Focus**: Asymmetric actor-critic architecture training legged robots to traverse unpredictable geometry, stairs, and discrete gaps.
- **Key Results**: Zero-shot sim-to-real transfer with decoded representations from raycaster LiDAR following ground-truth elevation.

### 2. Multi-Skill Jump and Bound Locomotion (IHMC Robotics Lab)
- **Tech**: NVIDIA Isaac Lab, PyTorch, Custom Reward Formulations
- **Focus**: Asymmetric actor-critic architecture training legged robots to distinctly transition between continuous running commands and dynamic jumping commands.
- **Key Results**: Zero-shot sim-to-real transfer with stable landing recovery and terrain adaptation.

---

# Graduate Coursework - Fall 2026

- **Foundations of Digital Signal Processing** (`EEE5502`) 
- **Fundamentals of Machine Learning** (`EEL5840`) 
- **Stochastic Methods of Engineering 1** (`EEE5544`) 

---

# Toolkit & Stack

- **Simulation & Robotics**: NVIDIA Isaac Lab, Isaac Sim, MuJoCo, ROS 2
- **Machine Learning**: PyTorch, ONNX, JAX, NumPy, SciPy, WandB
- **Languages & Tools**: Python, C++, CUDA, Docker, Git, Linux

---

# Contact

- **Email**: [christiancorona@ufl.edu](mailto:christiancorona@ufl.edu)
- **GitHub**: [github.com/chrisrcorona5](https://github.com/chrisrcorona5)
- **Location**: University of Florida, Gainesville, FL
