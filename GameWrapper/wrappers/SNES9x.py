import os
from pynput.keyboard import Controller, Key
import time
import subprocess
from PIL import Image
import keyboard
import numpy as np

from GameWrapper.wrappers.WrapperInterface import WrapperInterface, GAME_RESOLUTION
from GameWrapper.button.Buttons import BUTTONS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACT_FOLDER = "snes9x"
os.chdir(SCRIPT_DIR)
EXTRACT_PATH = os.path.join(SCRIPT_DIR, EXTRACT_FOLDER)
SNES9X_EXE = os.path.join(EXTRACT_PATH, "snes9x.exe")
ROM_PATH = os.path.join(SCRIPT_DIR, "snes9x/Roms/smw.sfc")
LUA_SCRIPT = os.path.join(SCRIPT_DIR, "bot.lua")
ROMS_FOLDER = os.path.join(EXTRACT_PATH, "Roms")
COLOR_IMAGE_PATH = "snes9x/Screenshots/smw000.png"
KEYMAP = {
    'A': 'v',
    'B': 'c',
    'X': 'd',
    'Y': 'x',
    'L': 'a',
    'R': 's',
    'UP': Key.up,
    'DOWN': Key.down,
    'LEFT': Key.left,
    'RIGHT': Key.right,
    'START': Key.space,
    'SELECT': Key.enter
}

class SNES9x(WrapperInterface):
    def __init__(self):
        self.is_ready = False
        self.keyboard = Controller()

    def launchEmulator(self):
        """
        Starts emulator (Does not launch the game)
        """
        if not os.path.exists(ROM_PATH) or not os.path.exists(SNES9X_EXE):
            raise RuntimeError("Please run emulator_initialize.py before using this wrapper!")

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
        print(f"Returning all 0's to caller. Please replace!")
        return np.zeros(shape=(*GAME_RESOLUTION, 1))


    def read16(self, address:int) -> np.int16:
        print(f"Reading 16 bits from address {hex(address)}")
        return np.int16(0)

    def read8(self, address:int) -> np.int8:
        print(f"Reading 8 bits from address {hex(address)}")
        return np.int8(0)