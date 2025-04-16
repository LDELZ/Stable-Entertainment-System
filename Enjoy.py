from stable_baselines3 import A2C

from GameWrapper.wrappers.SNES9x import SNES9x
from smw_environment import SmwEnvironment

if "__main__" in __name__:
    smw_env = SmwEnvironment(SNES9x())

    model = A2C.load("models_old/rl_smw_A2c__2000_steps_best.zip", smw_env)
    episodes = 0
    beat = 0
    died = 0
    times_up = 0
    wanted_episodes = 40
    #Since the environemnt gets wrapped by sb3
    env = model.get_env()
    obs = env.reset()
    for episodes in range(0, wanted_episodes + 1):
        term = False
        env.reset()
        while not term:
            action, state = model.predict(obs)
            obs, reward, term, info = env.step(action)
            term_reason = info[0]["term_reason"]
            if term:
                if term_reason == "Beat":
                    beat += 1
                elif term_reason == "Died":
                    died += 1
                else:
                    times_up += 1

    print("Statistics: ")
    print(f"Beat: {beat}\nDied: {died}\nTimed Out : {times_up}")
    print(f"Win rate: {beat/wanted_episodes * 100:.2f}")