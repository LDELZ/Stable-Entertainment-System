from typing import SupportsFloat, Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType, ActType
from pandas.core.interchange.from_dataframe import buffer_to_ndarray

from GameWrapper.wrappers.WrapperInterface import *
from GameWrapper.button.Buttons import BUTTONS, DIR_COMBOS

PROGRESS_COUNTDOWN_DEFAULT = 2.75 #Seconds

class SmwEnvironment(gym.Env):
    def __init__(self, wrapper:WrapperInterface, frame_skip:int=4):
        self.game_wrapper = wrapper
        self.observation_space = spaces.Dict({
            "rel_x": spaces.Box(0, 255, (1,), np.uint8),
            "screen" : spaces.Box(0, 255, (1, *GAME_RESOLUTION), np.uint8),
        })
        self.action_space = spaces.Box(0, 1, (len(BUTTONS),), np.uint8)
        self.frame_skip = frame_skip
        self.end_goal = (718, 350)
        self.farthest_progress = 0
        self.progress_countdown = 0 # Time since progress
        self.last_reward = 0

    def _get_obs(self):
        xpos = self.get_mario_pos()[0]
        rel_pos = np.round((self.end_goal[0] - xpos) / self.end_goal[0] * 255).astype(np.uint8)
        if rel_pos < 0:
           rel_pos = 0
        retDict = {"screen" : self.game_wrapper.screenshot(), "rel_x" : rel_pos}
        return retDict

    def step(
        self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        #Code for rewards go here
        print(action)
        buttons_to_send = [button for idx,button in enumerate(BUTTONS) if action[idx] >= 0.5 and button != "D"]
        #buttons_to_send.append(DIR_COMBOS[int(action[4])])

        self.game_wrapper.sendButtons(buttons_to_send)
        self.game_wrapper.advance(self.frame_skip)

        self.game_wrapper.populate_mem()
        obs = self._get_obs()
        print(obs["rel_x"])

        mario_vel = self.get_mario_speed()
        mario_pos = self.get_mario_pos()
        beat_level = self.game_wrapper.readu8(END_LVL_TIMER) != 0

        #Level progress
        if mario_pos[0] > self.farthest_progress:
            self.farthest_progress = mario_pos[0] + 30
            self.progress_countdown = 0
        else:
            self.progress_countdown += (1 / 60) * (self.frame_skip + 1)

        print(self.progress_countdown)

        timesup = self.progress_countdown >= PROGRESS_COUNTDOWN_DEFAULT


        mario_dead = self.game_wrapper.readu8(ANIM_TRIGGER_STATE) == PLAYER_DEAD_VAL
        if mario_dead:
            print("Mario died!")

        reward = 0
        punishment = 0

        #Calculate the reward
        diffInPos = np.subtract(mario_pos, self.end_goal)
        diffInVel = np.multiply(mario_vel, (1, 1))
        distAway  = np.sqrt(diffInPos.dot(diffInPos))
        closingVel = - (diffInPos.dot(diffInVel)) / distAway

        reward = (1.8 * closingVel + 1.1 * closingVel ** 2)
        reward += 30 * beat_level
        #punishment += 200 * mario_dead
        punishment += 30 * timesup


        term_reason = "None"
        if beat_level:
            term_reason = "Beat"
        elif timesup:
            term_reason = "TimeUp"
        elif mario_dead:
            term_reason = "Died"

        self.last_reward = reward

        print(f"Mario is at ({mario_pos[0]}, {mario_pos[1]})")

        print(f"Reward: {reward}\nPunishment: {punishment}")

        return obs, reward - punishment, mario_dead or beat_level or timesup, False, {"term_reason" : term_reason}

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
        self.farthest_progress = 0
        self.progress_countdown = 0
        self.last_reward = 0

        return self._get_obs(), {}
