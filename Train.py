'''
******************************************************************************
 * File:        Train.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: Initializes the SmwEnvironment gymnasium game environment, SAC
                algorithm, and performs training for 500 steps. Uses a 
                multi-layer perceptron policy, logs outputs to log files, and 
                performs training using the CPU.
 * Usage:       Run this program in a Python 3.12.x or higher environment.
 ******************************************************************************
 '''

# Import Stable Baselines 3 (SB3) checkpoint callbacks and A2C algorithm
# Import the Game Wrapper and gynasium environments
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3 import A2C
from smw_environment import SmwEnvironment
from GameWrapper.wrappers.SNES9x import SNES9x
import sys
from datetime import datetime

# Generate the name of the current model using the current date-time
checkpoint_name = datetime.now().strftime("rl_smw_A2c_")

# Appends the arguments used during training to the checkpoint name
if len(sys.argv) >= 2:
    checkpoint_name = sys.argv[1]

# Save the model for each 1000 training steps performed in the models/ directory
# Save the replay buffer and vector statistics for normalization of observations and rewards
checkpoint_callback = CheckpointCallback(
    save_freq=1000,
    save_path="./models/",
    name_prefix=f"{checkpoint_name}",
    save_replay_buffer=True,
    save_vecnormalize=True,
)
print(f"Saving models to models/{checkpoint_name}")

'''
------------------------------------------------------------------------------
* Function: main
* --------------------
* Description:
*	Initializes the gymnasium game environment (SmwEnvironment) and model
    using the A2C algorithm. Specifies the A2C arguments. MultiInputPolicy
    enables dictionary observations for the screenshot and positional values,
    verbose stores the log outputs in files, cuda enables GPU accelerated
    training, enables tensorboard log statistic visualization, and preserves
    the screenshot as raw pixel inputs. Trains the agent for 15,000 steps
*
* Arguments:   none
* Returns:     none
'''
if "__main__" in __name__:
    env = SmwEnvironment(SNES9x())
    model = A2C("MultiInputPolicy", 
                env, 
                verbose=1, 
                device="cuda", 
                tensorboard_log="./logdata/", 
                policy_kwargs=dict(normalize_images=False))
    
    # Start training for 15,000 steps, log every 4 steps, save checkpoints
    model.learn(total_timesteps=int(15000), log_interval=4, callback=checkpoint_callback)