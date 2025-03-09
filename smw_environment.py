from typing import SupportsFloat, Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType, ActType
from GameWrapper.wrappers.WrapperInterface import WrapperInterface, GAME_RESOLUTION
from GameWrapper.button.Buttons import BUTTONS

class SmwEnvironment(gym.Env):
    def __init__(self, wrapper:WrapperInterface, frame_skip:int=4):
        self.game_wrapper = wrapper
        self.observation_space = spaces.Box(0, 255, (*GAME_RESOLUTION, 1), np.uint8)
        self.action_space = spaces.Box(0, 1, (len(BUTTONS),), np.uint8)
        self.frame_skip = frame_skip

    def _get_obs(self):
        return self.game_wrapper.screenshot()

    def step(
        self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        #Code for rewards go here

        obs = self._get_obs()
        terminate = False
        reward = 0

        buttons_to_send = [button for idx,button in enumerate(BUTTONS) if action[idx] == 1]

        self.game_wrapper.sendButtons(buttons_to_send)
        self.game_wrapper.advance(self.frame_skip)

        return obs, reward, terminate, False, {}

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        if not self.game_wrapper.is_ready:
            self.game_wrapper.launchEmulator()
            self.game_wrapper.startGame()

        self.game_wrapper.loadState("state")

        return self._get_obs(), {}
