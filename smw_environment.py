from typing import SupportsFloat, Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType, ActType
from GameWrapper.wrappers.WrapperInterface import WrapperInterface, GAME_RESOLUTION
from GameWrapper.button.Buttons import ALL_BUTTONS, Button

class SmwEnvironment(gym.Env):
    def __init__(self, wrapper:WrapperInterface):
        self.game_wrapper = wrapper

        self.observation_space = spaces.Box(0, 255, (*GAME_RESOLUTION, 3), np.uint8)
        self.action_space = spaces.Box(0, 1, (len(ALL_BUTTONS),), np.uint8)

    def _get_obs(self):
        return self.game_wrapper.getframe()

    def step(
        self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        #Code for rewards go here

        obs = self._get_obs()
        terminate = False
        reward = 0
        #Rounded action

        #Figure out which buttons to send
        buttons_to_send:list[Button] = []
        for idx, button in enumerate(ALL_BUTTONS):
            if action[idx] == 1:
                buttons_to_send.append(button)

        self.game_wrapper.sendkeys(buttons_to_send)
        self.game_wrapper.advanceframe()

        return obs, reward, terminate, False, {}

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        self.game_wrapper.loadstate("state")

        return self._get_obs(), {}
