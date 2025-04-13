from typing import SupportsFloat, Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType, ActType
from GameWrapper.wrappers.WrapperInterface import *
from GameWrapper.button.Buttons import BUTTONS

class SmwEnvironment(gym.Env):
    def __init__(self, wrapper:WrapperInterface, frame_skip:int=4):
        self.game_wrapper = wrapper
        self.observation_space = spaces.Box(0, 255, (*GAME_RESOLUTION,), np.uint8)
        self.action_space = spaces.Box(0, 1, (len(BUTTONS),), np.uint8)
        self.frame_skip = frame_skip
        self.end_goal = (4808, 352)

    def _get_obs(self):
        return self.game_wrapper.screenshot()

    def step(
        self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        #Code for rewards go here
        obs = self._get_obs()
        self.game_wrapper.populate_mem()
        mario_vel = self.get_mario_speed()
        mario_pos = self.get_mario_pos()
        beat_level = self.game_wrapper.readu8(END_LVL_TIMER) != 0

        mario_dead = self.game_wrapper.readu8(ANIM_TRIGGER_STATE) == 9
        if mario_dead:
            print("Mario died!")

        reward = 0
        punishment = 0

        #Calculate the reward
        diffInPos = np.subtract(mario_pos, self.end_goal)
        diffInVel = mario_vel
        distAway  = np.sqrt(diffInPos.dot(diffInPos))
        closingVel = - (diffInPos.dot(diffInVel)) / distAway

        reward = 4 * closingVel + 8 * closingVel ** 2
        reward += 100 * beat_level
        punishment += 200 * mario_dead


        print(f"Mario is at ({mario_pos})")

        buttons_to_send = [button for idx,button in enumerate(BUTTONS) if action[idx] == 1]

        self.game_wrapper.sendButtons(buttons_to_send)
        self.game_wrapper.advance(self.frame_skip)

        print(f"Reward: {reward}\nPunishment: {punishment}")

        return obs, reward - punishment, mario_dead or beat_level, False, {}

    def get_mario_speed(self) -> tuple[np.float32, np.float32]:
        x_vel = np.int8(self.game_wrapper.readu8(X_VEL)) * np.float32(1 / 16)
        y_vel = -np.int8(self.game_wrapper.readu8(Y_VEL)) * np.float32(1 / 16) # Because up is negative
        return x_vel, y_vel

    def get_mario_pos(self) -> tuple[np.uint16, np.uint16]:
        return self.game_wrapper.readu16(X_ADDR), self.game_wrapper.readu16(Y_ADDR)


    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        if not self.game_wrapper.is_ready:
            self.game_wrapper.startGame()

        self.game_wrapper.loadState("state")

        return self._get_obs(), {}
