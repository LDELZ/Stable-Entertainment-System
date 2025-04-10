from stable_baselines3 import SAC, A2C
from smw_environment import SmwEnvironment
from GameWrapper.wrappers.SNES9x import SNES9x

if "__main__" in __name__:
    env = SmwEnvironment(SNES9x(disable_keys=False))
    model = SAC("MlpPolicy", env, verbose=1, buffer_size=1, device="cpu")

    model.learn(total_timesteps=500)