import numpy as np
from GameWrapper.button.Buttons import *

GAME_RESOLUTION = (224,256)
X_ADDR = 0x7E00D1
Y_ADDR = 0x7E00D3
X_VEL = 0x7E007B
Y_VEL = 0x7E007D
ANIM_TRIGGER_STATE = 0x7E0071
END_LVL_TIMER = 0x7E1493
PLAYER_PIECE = 28 # Will be 0 up until level is beat
PLAYER_DEAD_VAL = 0x09
PLAYER_HURT_VAL = 0x01

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
        return np.zeros(shape=(*GAME_RESOLUTION,))

    def populate_mem(self) -> None:
        print(f"Populating memory")
        return

    def readu16(self, address:int) -> np.uint16:
        print(f"Reading 16 bits from address {hex(address)}")
        return np.uint16(0)

    def readu8(self, address:int) -> np.uint8:
        print(f"Reading 8 bits from address {hex(address)}")
        return np.uint8(0)
