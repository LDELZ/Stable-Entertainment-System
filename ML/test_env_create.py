from stable_baselines3 import SAC
from smw_environment import SmwEnvironment
from GameWrapper.wrappers.DummyWrapper import DummyWrapper

if "__main__" in __name__:
    env = SmwEnvironment(DummyWrapper())
    model = SAC("MlpPolicy", env, verbose=1, buffer_size=1, device="cuda")

    model.learn(total_timesteps=500)