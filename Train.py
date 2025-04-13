from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3 import A2C
from smw_environment import SmwEnvironment
from GameWrapper.wrappers.SNES9x import SNES9x
import sys
from datetime import datetime

checkpoint_name = datetime.now().strftime("rl_smw_A2c_%m-%d-%y_%I_%M:%S")

if len(sys.argv) >= 2:
    checkpoint_name = sys.argv[1]

checkpoint_callback = CheckpointCallback(
    save_freq=20000,
    save_path=".",
    name_prefix=f"models/{checkpoint_name}",
    save_replay_buffer=True,
    save_vecnormalize=True,
)

print(f"Saving models to models/{checkpoint_name}")

if "__main__" in __name__:
    env = SmwEnvironment(SNES9x())
    model = A2C("MlpPolicy", env, verbose=1, device="cpu",  tensorboard_log="./logdata/")

    model.learn(total_timesteps=int(2.6 * 10 **5), log_interval=4, callback=checkpoint_callback)