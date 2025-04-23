'''
******************************************************************************
 * File:        test_env_create.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: Initializes the SmwEnvironment gymnasium game environment, SAC
                algorithm, and performs training for 500 steps. Uses a 
                multi-layer perceptron policy, logs outputs to log files, and 
                performs training using the CPU.
 * Usage:       This program is automatically used by the Train.pt and Enjoy.py
                programs and is not intended for use on its own.
 ******************************************************************************
 '''

# Import Stable Baselines 3's soft actor-critic algorithm
# Import the game environment and game wrapper
from stable_baselines3 import SAC
from smw_environment import SmwEnvironment
from GameWrapper.wrappers.SNES9x import SNES9x

'''
------------------------------------------------------------------------------
* Function: main
* --------------------
* Description:
*	Initializes the gymnasium game environment (SmwEnvironment), SAC algorithm,
    and performs training for 500 steps. Uses a multi-layer perceptron policy,
    logs outputs to log files, and performs training using the CPU.
*
* Arguments:   none
* Returns:     none
'''
if "__main__" in __name__:
    env = SmwEnvironment(SNES9x())
    model = SAC("MlpPolicy", env, verbose=1, buffer_size=1, device="cpu")
    model.learn(total_timesteps=500)