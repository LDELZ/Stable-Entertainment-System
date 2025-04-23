'''
******************************************************************************
 * File:        smw_environment.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: This program specifies the Stable Baselines 3 (SB3) gym 
                environment. It runs Super Mario World in the SNES9x-rr 
                emulator and supports training models, and running tests in 
                the game environment. It uses the gymnasium library and the 
                custom GameWrapper to pass screenshot data, the memory values,
                button inputs, and rewards between SB3 and SNES9x-rr
 * Usage:       This program is automatically used by the Train.pt and Enjoy.py
                programs and is not intended for use on its own.
 ******************************************************************************
 '''

# Import the gymnasium environment, custom Game Wrapper, and data decoders
from typing import SupportsFloat, Any
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType, ActType
from pandas.core.interchange.from_dataframe import buffer_to_ndarray
from GameWrapper.wrappers.WrapperInterface import *
from GameWrapper.button.Buttons import BUTTONS, DIR_COMBOS

# Set the progrss timer constant (in seconds)
# This is used to timeout the current episode if progress cannot be made
PROGRESS_COUNTDOWN_DEFAULT = 2.75

'''
------------------------------------------------------------------------------
 * Class: SmwEnvironment
 * --------------------
 * Description:
 *	Represents an instance of the Super Mario World game environment that
    integrates SB3 and SNES9x-rr agent control
 '''
class SmwEnvironment(gym.Env):

    '''
    ------------------------------------------------------------------------------
    * Function: SmwEnvironment constructor
    * --------------------
    * Description:
    *	Initializes the game wrapper interface, the game resolution, the relative
        position of Mario to the goal post, the goal position, the timeout counter,
        the actions that SB3 is allowed to take in the agent, and the reward.
    *
    * Arguments:   A WrapperInterface object; number of frames to skip per advance
    * Returns:     none
    '''
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

    '''
    ------------------------------------------------------------------------------
    * Function: SmwEnvironment _get_obs
    * --------------------
    * Description:
    *	Gets the observation that will be sent to the SB3 reinforcement learning
        agent. Returns values necessary for determining the next set of inputs
        to improve game performance on. A screenshot of the game window and the
        normalized distance between
    *
    * Arguments:   none
    * Returns:     none
    '''
    def _get_obs(self):

        # Get Mario's absolute position
        xpos = self.get_mario_pos()[0]

        # Determine how far Mario is from the goal
        rel_pos = np.round((self.end_goal[0] - xpos) / self.end_goal[0] * 255).astype(np.uint8)

        # Make sure Mario has not somehow gone past the goal without the game documenting a win
        if rel_pos < 0:
           rel_pos = 0
        
        # Generate a dictionary of the current screenshot and Mario's relative goal position
        retDict = {"screen" : self.game_wrapper.screenshot(), "rel_x" : rel_pos}

        # Return the dictionary to be used by SB3
        return retDict

    '''
    ------------------------------------------------------------------------------
    * Function: SmwEnvironment step
    * --------------------
    * Description:
    *	Performs a gym environment step. This applies a game action, frame
        advances SNES9x-rr to the next frame, calculates the reward from the action,
        and passes the information to SB3.
    *
    * Arguments:    An action Numpy array of button inputs (ActType)
    * Returns:      An observation dictionary of the screenshot values and Mario's position
                    The reward amount calculated from the velocity, progrss, bonuses, and penalties
                    A boolean for whether the episode has ended
                    A boolean for if the episode was terminated early
                    A dictionary of the term indicating the event that caused the episode to end
    '''
    def step(self, action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:

        # Display the current action to be taken this step
        print(action)

        # Enumerate the buttons in the action and determine if they are pressed (>0.5)
        buttons_to_send = [button for idx,
                           button in enumerate(BUTTONS) if action[idx] >= 0.5 and button != "D"]

        # Send the buttons to be pressed by the joypad in the emulator
        # Advance emulatoro frames holding those buttons
        self.game_wrapper.sendButtons(buttons_to_send)
        self.game_wrapper.advance(self.frame_skip)

        # Get the table of memory values specified in memory_server.lua
        self.game_wrapper.populate_mem()

        # Get Mario's position relative to the goal post
        obs = self._get_obs()
        print(obs["rel_x"])

        # Get Mario's velocity and position
        mario_vel = self.get_mario_speed()
        mario_pos = self.get_mario_pos()

        # Determine if Mario reached the goal this step and the level timer is not expired
        beat_level = self.game_wrapper.readu8(END_LVL_TIMER) != 0

        # Determine if Mario has made progress this step by checking if the current position
        # is farther than the previous best position.
        # Add 30 pixels to the position to prevent false flagging of Mario being stuck
        if mario_pos[0] > self.farthest_progress:
            self.farthest_progress = mario_pos[0] + 30
            self.progress_countdown = 0

        # Otherwise Mario has not made progress, increment countdown timer by the number advanced frames
        # When the timer reaches the timout for progress, stop the episode
        else:
            self.progress_countdown += (1 / 60) * (self.frame_skip + 1)

        # Display how much time is remaining to make progress
        print(self.progress_countdown)

        # Set the times-up flag if no progres was made in time
        timesup = self.progress_countdown >= PROGRESS_COUNTDOWN_DEFAULT

        # Determine if Mario dies and set the corresponding flag
        mario_dead = self.game_wrapper.readu8(ANIM_TRIGGER_STATE) == PLAYER_DEAD_VAL
        if mario_dead:
            print("Mario died!")

        # Calculate the reward
        reward = 0
        punishment = 0
        diffInPos = np.subtract(mario_pos, self.end_goal)
        diffInVel = np.multiply(mario_vel, (1, 1))
        distAway  = np.sqrt(diffInPos.dot(diffInPos))
        closingVel = - (diffInPos.dot(diffInVel)) / distAway

        reward = (1.8 * closingVel + 1.1 * closingVel ** 2)

        # Apply a bonus or punishment: +30 for beating the level, -30 for not progressing
        reward += 30 * beat_level
        #punishment += 200 * mario_dead
        punishment += 30 * timesup

        # Match the set flags to the appropriate dictionary term to indicate to SB3 why the episode ended
        term_reason = "None"
        if beat_level:
            term_reason = "Beat"
        elif timesup:
            term_reason = "TimeUp"
        elif mario_dead:
            term_reason = "Died"

        # Store the reward for the previous episode
        self.last_reward = reward

        # Display and return the position and reward values, flags, and return the screenshot
        print(f"Mario is at ({mario_pos[0]}, {mario_pos[1]})")
        print(f"Reward: {reward}\nPunishment: {punishment}")
        return obs, reward - punishment, mario_dead or beat_level or timesup, False, {"term_reason" : term_reason}

    '''
    ------------------------------------------------------------------------------
    * Function: SmwEnvironment get_mario_speed
    * --------------------
    * Description:
    *	Obtains and returns Mario's current velocity from the in-game memory values.
    *
    * Arguments:    none
    * Returns:      A tuple of the x and y velocities. Note that due to the way
                    SNES games are rendered, moving upward is actually a negative
                    speed value, meaning that jump movement is negative. Positive
                    velocity is therefore found by negating the upward negative
                    movement.
    '''
    def get_mario_speed(self) -> tuple[np.float32, np.float32]:
        x_vel = np.int8(self.game_wrapper.readu8(X_VEL)) * np.float32(1 / 16)
        y_vel = -np.int8(self.game_wrapper.readu8(Y_VEL)) * np.float32(1 / 16)
        return x_vel, y_vel

    '''
    ------------------------------------------------------------------------------
    * Function: SmwEnvironment get_mario_pos
    * --------------------
    * Description:
    *	Obtains and returns Mario's current position from the in-game memory values.
    *
    * Arguments:    none
    * Returns:      A tuple of the x and y positions
    '''
    def get_mario_pos(self) -> tuple[np.uint16, np.uint16]:
        return self.game_wrapper.readu16(X_ADDR), self.game_wrapper.readu16(Y_ADDR)

    '''
    ------------------------------------------------------------------------------
    * Function: SmwEnvironment reset
    * --------------------
    * Description:
    *	Resets the environment after each episode. This function is required for 
        gymnasium environments. It enables random gym seeding and options which are
        not required foro this project.
    *
    * Arguments:    seed and option values
    * Returns:      A tuple of the screenshot and distance to goal
    '''
    def reset(self, 
              *, 
              seed: int | None = None, 
              options: dict[str, Any] | None = None,) -> tuple[ObsType, dict[str, Any]]:
        
        # Start the emulator game environment if it is not running
        if not self.game_wrapper.is_ready:
            self.game_wrapper.startGame()

        # Load the save state
        self.game_wrapper.loadState("state")

        # Reset progress and reward values
        self.farthest_progress = 0
        self.progress_countdown = 0
        self.last_reward = 0

        # Return the initial observation from _get_obs including screenshot and position
        return self._get_obs(), {}
