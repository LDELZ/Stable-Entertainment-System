import numpy as np
from GameWrapper.button.Buttons import *

GAME_RESOLUTION = (256, 224)

class WrapperInterface():
    def __init__(self):
        pass

    def sendkeys(self, key_list:list[Button]):
        raise RuntimeError("Please subclass the wrapper interface to use sendkeys")

    def advanceframe(self):
        raise RuntimeError("Please subclass the wrapper interface to use advanceframe")

    def loadstate(self, state_name:str):
        raise RuntimeError("Please subclass the wrapper interface to use loadstate")

    def getframe(self) -> np.array:
        raise RuntimeError("Please subclass the wrapper interface to use getframe")

    def read16(self, address:int) -> np.int16:
        raise RuntimeError("Please subclass the wrapper interface to use read16")