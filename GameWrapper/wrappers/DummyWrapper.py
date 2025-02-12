import numpy as np

from GameWrapper.wrappers.WrapperInterface import WrapperInterface, GAME_RESOLUTION
from GameWrapper.button.Buttons import Button


class DummyWrapper(WrapperInterface):
    def __init__(self):
        super().__init__()

    def sendkeys(self, key_list:list[Button]):
        print("Sending keys: ", end='')
        for key in key_list:
            print(f"{key}", end=' ')
        print("")

    def getframe(self) -> np.array:
        return np.zeros(shape=(*GAME_RESOLUTION, 3))

    def loadstate(self, state_name:str):
        print(f"Fake loading state {state_name}")

    def advanceframe(self):
        print(f"Advancing Frame")

    def read16(self, address:int) -> np.int16:
        return np.int16(0)