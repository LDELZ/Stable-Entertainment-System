'''
******************************************************************************
 * File:        Enjoy.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: This program runs a trained SB3 model in the custom game
                environment and the GameWrapper for agent control. It
                uses the Stable Baselines 3 (SB3) library to run the model
                and controls the emulator agent through the wrapper.
                Statistics are automatically computed and displayed.
 * Usage:       Run this program in a Python 3.11.x or higher environment.
                A valid model must be present in the models/ directory in
                order for model testing to function.
 ******************************************************************************
 '''

# Import Stable Baselines 3 and requirements
from stable_baselines3 import A2C
from GameWrapper.wrappers.SNES9x import SNES9x
from smw_environment import SmwEnvironment
import numpy as np

'''
------------------------------------------------------------------------------
* Function: main
* --------------------
* Description:
*	Initializes and runs a trained model; computes test performance statistics
*
* Arguments:   none
* Returns:     none
'''
if "__main__" in __name__:

    # Initialize the SNES9x game environment
    smw_env = SmwEnvironment(SNES9x())

    # Load the trained A2C model in the models/ directory
    model = A2C.load("models/rl_smw_A2c__2000_steps_best.zip", smw_env)

    # Initialize performance value accumulators
    episodes = 0
    beat = 0
    died = 0
    times_up = 0
    wanted_episodes = 1

    # Initialize a list of reward values per step
    reward_totals = []

    # Initialize a new game environment wrapped by SB3
    # Reset all environment objects
    env = model.get_env()
    obs = env.reset()

    # For each episode in the desired number of episodes,
    # Check if a term value for an event exists (e.g. Mario 'beat' the level)
    for episodes in range(0, wanted_episodes):
        term = False
        reward_totals.append(0)

        # While a term does not exist, predict the next inputs
        # Perform a step to the next frame and store the step results
        while not term:
            action, state = model.predict(obs)
            obs, reward, term, info = env.step(action)
            reward_totals[-1] += reward

            # Obtain result of othe current episode from the info data
            # Match the term to the event that occurred
            # Accumulate the corresponding counter
            term_reason = info[0]["term_reason"]
            if term:
                if term_reason == "Beat":
                    beat += 1
                elif term_reason == "Died":
                    died += 1
                else:
                    times_up += 1

    # Output the performance statistics to the console
    # This includes times beaten, times died, the win rate, and average reward
    print("Statistics: ")
    print(f"Beat: {beat}\nDied: {died}\nTimed Out : {times_up}")
    print(f"Win rate: {beat/wanted_episodes * 100:.2f}")
    print(f"Avg. Reward: {np.sum(reward_totals) / len(reward_totals)}")