# Stable Entertainment System

**Authors**: Brennan Romero, Luke Delzer  

## Overview

Stable Entertainment System (SES) is an on-policy agent training model that automates gameplay for the Super Nintendo Entertainment System (SNES). It uses [Stable Baselines 3 (SB3)](https://github.com/DLR-RM/stable-baselines3) and the [A2C](https://arxiv.org/abs/2205.09123) algorithm to learn how to play SNES games in the [SNES9x-rr](https://github.com/gocha/snes9x-rr/releases) emulator. SES was designed to automate gameplay for the game Super Mario World but supports extensibility to other SNES games.

## Key Topics

- **Agent Systems**
- **Reinforcement Learning**
- **Deep Reinforcement Learning**
- **Policy Gradients**

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Training Details](#training-details)
- [Results](#results)
- [Project Structure](#project-structure)
- [Legal Notice](#legal-notice)
- [License](#license)
- [References](#references)

## Description
This program automates installation and configuration of SB3 and SNES9x-rr emulator agents. Once installed, execution of the program creates an image-action pipeline that captures screenshots from the emulator, passes a data matrix of the image to SB3, processes the image to determine the inputs to be held during the next frame, and advances frames holding those inputs. A video file is automatically generated for the finalized gameplay.

SNES9x-rr leverages [Lua](#https://www.lua.org/manual/5.4/) scripting to enable frame-specific game control within the emulator. [LuaSocket](https://lunarmodules.github.io/luasocket/) interfaces with Python for sending and receiving game data between agents over TCP. A custom Lua script retrieves memory values directly from the game as specified in the "Memory Watch" variable in lua_script.lua. The memory values and screenshot are passed to the SB3 environment. Once the next set of inputs is determind, they are passed back over the TCP LuaSocket connection to be processed by the emulator. The inputs are held during five successive frame advances, when a new screenshot is generated for the next iteration.

Need real-time learning from current game state (on-policy):
Similar to human abilities: learn from gameplay, update current strategy
Must be faster than off-policy algorithms: appeal to customers / end-users
Asynchronous Advantage Actor Critic (A2C):
Actor performs an action and critic evaluates it
Successful actions encouraged, unsuccessful discouraged (forms policy)
Actor maximizes reward, performs successful actions
Advantages:
Works well with discrete action spaces
Can inject entropy into objective function to prevent determinism
Performs at least as good as DQN for Atari games (Le et al., 2021)

## Features
Game environment is more complex than previous studies:
Broad range of colors, high pixel density, advanced physics, diverse gameplay goals
Frames are more information-dense (i.e detailed backgrounds, enemy movement, diverse terrain)
Features useful to the model must be extracted from the frames (i.e. enemy positions, terrain)
Utilizing a Novel Framework
Stable Baselines 3 implements various RL algorithms with strong performance
Algorithms are model-free; no need to worry about underlying architecture
Improve results in complicated environments:
Beneficial for externalizing to challenging data-dense environments (i.e. surgery, self-driving cars)
SNES Mario makes this project applicable for testing and developing modern 2D platformers
Greenfield project: novel model previously unstudied in modern 2D platformers
Uses Sethbling’s performance as a baseline but with a completely distinct approach
Project requires no prior gameplay data
Performs actions at a human-achievable rate
Algorithm choices are not tied to specific model architecture
Model requires mostly visual inputs
Uses policies inspired by drone navigation studies

## Software Utilized

- [**SNES9X-rr v1.51**](https://github.com/gocha/snes9x-rr)  
  A modified version of the SNES9X emulator that enables recordings and Lua scripting. This serves as the agent.
  *License: Freeware for personal use; GPL/LGPL for included components (JMA, snes_ntsc, xBRZ)*

- [**Stable Baselines3 (SB3)**](https://github.com/DLR-RM/stable-baselines3)  
  A machine learning framework used to implement actor-critic algorithms with strong results.
  *License: MIT*

- [**Python**](https://github.com/python/cpython)  
  Interfaces the emulator and machine learning agents.
  *License: Python Software Foundation License (PSF License)*

## Demo
<table>
  <tr>
    <td>
      <img src="sb3_final.gif" alt="Super Mario World AI Demo" width="320">
    </td>
    <td style="padding-left: 20px;">
      <img src="table.png" alt="Agent Performance Summary" width="320">
    </td>
  </tr>
</table>


## Legal Notice

This project is intended for research and educational purposes only. We **do not condone or support software piracy** of any kind. Any references to Super Mario World or other game ROMs are made strictly in the context of technical compatibility and emulator integration for reinforcement learning research. SES requires a legitimately-obtained ROM file for Super Mario World, or any other game you wish to automate. No ROM files are provided, and any ROM must be obtained on the user's own volition. We recommend obtaining these files only through completely legitimate means. It is your responsibility to ensure that you comply with all applicable local, national, and international copyright laws when obtaining ROM files for automation. This project **does not provide or distribute any copyrighted ROM files**, and we **stand strongly against piracy** in any form.

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).  
You may use, modify, and distribute this software in compliance with the license terms. See the `LICENSE` file for more details.



## References

- [Quadcopter Guidance Law Design using Deep Reinforcement Learning (Aydinli & Kutay, 2023)](https://doi.org/10.1109/RAST57548.2023.10197848)
- [Deep Reinforcement Learning in Computer Vision: A Comprehensive Survey (Le et al., 2021)](https://arxiv.org/abs/2108.11510)
- [Playing Atari with Deep Reinforcement Learning (Mnih et al., 2013)](https://arxiv.org/abs/1312.5602)
- [Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning (Haarnoja et al., 2018)](https://arxiv.org/abs/1801.01290)
- [A2C Is a Special Case of PPO (Huang et al., 2022)](https://arxiv.org/abs/2205.09123)
- [Stable-Baselines3: Reliable Reinforcement Learning Implementations (Raffin et al., 2021)](https://www.jmlr.org/papers/v22/20-1364.html)
- [MarI/O - Machine Learning for Video Games (SethBling, 2015)](https://www.youtube.com/watch?v=qv6UVOQ0F44)
- [Proximal Policy Optimization Algorithms (Schulman et al., 2017)](https://arxiv.org/abs/1707.06347)
- [AI for Classic Video Games using Reinforcement Learning (Sodhi, 2017)](https://scholarworks.sjsu.edu/etd_projects/538)

