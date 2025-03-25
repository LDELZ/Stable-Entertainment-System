import numpy as np
from GameWrapper.button.Buttons import *

GAME_RESOLUTION = (256, 224)

class WrapperInterface():
    def __init__(self):
        self.is_ready = False

    def launchEmulator(self):
        """
        Starts emulator (Does not launch the game)
        """
        print("Launching Emulator!")

    def startGame(self):
        """
        Navigates the emulator to load the game and take the initial savestate. Sets up any lua scripts
        """
        print("Starting Game!")

    def sendButtons(self, key_list:list[str]):
        """
        Sends the buttons to the emulator. Any button not pushed should be released
        """
        print(f"Sending buttons {key_list}")

    def releaseAllButtons(self):
        self.sendButtons([])

    def advance(self, n:int):
        """
        Advances the emulator by n frames
        """
        print(f"Advancing by 1 + {n-1} frames!")

    def loadState(self, state_name:str):
        """
        Make the emulator load some system state called state_name
        """
        print(f"Loading save state {state_name}...")

    def saveState(self, state_name:str):
        """
        Make the emulator save the system state in a state called state_name
        """
        print(f"Saving state to {state_name}...")

    def screenshot(self) -> np.array:
        """
        Take a screenshot. (Convert to grayscale)
        """
        print(f"Taking a screenshot!")
        return np.zeros(shape=(*GAME_RESOLUTION, 1))


    def read16(self, address:int) -> np.int16:
        print(f"Reading 16 bits from address {hex(address)}")
        return np.int16(0)

    def read8(self, address:int) -> np.int8:
        print(f"Reading 8 bits from address {hex(address)}")
        return np.int8(0)