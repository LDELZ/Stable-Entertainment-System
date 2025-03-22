import os
from pynput.keyboard import Controller, Key
import time
import subprocess
from PIL import Image
import keyboard
import numpy as np
import pygetwindow as gw
import win32gui
import win32con
from GameWrapper.wrappers.WrapperInterface import WrapperInterface, GAME_RESOLUTION
from GameWrapper.button.Buttons import BUTTONS

# Set the current directory as the script execution directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Paths
SNES9X_EXE = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/snes9x.exe"))
ROM_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Roms/smw.sfc"))
SCREENSHOTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Screenshots"))
SCREENSHOTS_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Screenshots/smw000.png"))
SAVESTATE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Saves/smw.000"))

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
        self.process = None
        self.n = 5

    def pressButton(self, button):
        key = KEYMAP.get(button, button)
        self.keyboard.press(key)
        time.sleep(0.1)
        self.keyboard.release(key)
        
    def launchEmulator(self):
        """
        Starts emulator (Does not launch the game)
        """
        if not os.path.exists(SNES9X_EXE):
            raise RuntimeError("Please run emulator_initialize.py before using this wrapper!")

        try:
            self.process = subprocess.Popen([SNES9X_EXE])
            self.is_ready = True
            print("SNES9x launched.")
        except Exception as e:
            raise RuntimeError(f"Failed to launch SNES9x: {e}")

        time.sleep(1)
        if self.process and self.process.poll() is None:
            print("Closing SNES9x emulator...")
            self.process.terminate()
            self.process.wait()
            self.is_ready = False

    def startGame(self):
        """
        Navigates the emulator to load the game and take the initial savestate. Sets up any lua scripts
        """
        print("Starting Game!")

        # Ensure the ROM file still exists in the Roms folder
        if not os.path.exists(ROM_PATH):
            raise FileNotFoundError(f"ROM not found at: {ROM_PATH}")

        for filename in os.listdir(SCREENSHOTS_DIR):
            file_path = os.path.join(SCREENSHOTS_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Open the emulator with the SMW ROM
        subprocess.Popen([SNES9X_EXE, ROM_PATH])

        # Bring the SNES9x window to the foreground so it can receive keyboard input
        for window in gw.getWindowsWithTitle('snes9x'):
                win32gui.ShowWindow(window._hWnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(window._hWnd)
                print("SNES9x window focused.")
        
        #Remove the background layer
        time.sleep(1)
        self.pressButton('2')

        # Take first screenshot
        self.pressButton(Key.f12)

        if not os.path.exists(SAVESTATE_PATH):
            print("No savestate found! Creating new Level 1 savestate.")
            # Get the level 1 savestate
            time.sleep(5)
            for _ in range(4):
                self.pressButton(Key.space)
                time.sleep(0.5)
            time.sleep(2)
            self.pressButton(Key.left)
            time.sleep(2)
            self.pressButton('A')
            time.sleep(3)
            self.saveState("smw.000")
        else:
            print("Savestate found! Loading current savestate")
            self.loadState("smw.000")

        # Enter frame-advance mode
        self.pressButton("\\")

        while True:
            self.advance(self.n)
            self.screenshot()
            

    def sendButtons(self, key_list:list[str]):
        """
        Sends the buttons to the emulator. Any button not pushed should be released
        """
        print(f"Sending buttons {key_list}")

        '''
        THIS IS MY OLD FUNCTION; I WILL BE WORKING THIS FUNCTIONALITY INTO THIS NEW FUNCTION SOON
        for key in inputs:
            mapped_key = KEYMAP[key]
            print(f"Pressing: {mapped_key}")

            # Press and release the key
            KEYBOARD.press(mapped_key)'
        '''

    def releaseAllButtons(self):
        self.sendButtons([])

    def advance(self, n:int):
        """
        Advances the emulator by n frames
        """
        print(f"Advancing by 1 + {n-1} frames!")
        time.sleep(1)
        for _ in range(n):
            self.pressButton("\\")

    def loadState(self, state_name:str):
        """
        Make the emulator load some system state called state_name
        """
        self.keyboard.press(Key.f1)
        time.sleep(0.1)
        self.keyboard.release(Key.f1)
        print(f"Loading save state {state_name}...")

    def saveState(self, state_name:str):
        """
        Make the emulator save the system state in a state called state_name
        """
        self.keyboard.press(Key.shift)
        self.keyboard.press(Key.f1)
        time.sleep(0.1)
        self.keyboard.release(Key.f1)
        self.keyboard.release(Key.shift)
        print(f"Saving state to {state_name}...")

    def screenshot(self) -> np.array:
        """
        Take a screenshot. (Convert to grayscale)
        """
        self.pressButton(Key.f12)
        time.sleep(1)

        if not os.path.exists(SCREENSHOTS_PATH):
            raise FileNotFoundError(f"Screenshot not found at: {SCREENSHOTS_PATH}")

        # Open and convert to grayscale
        img_color = Image.open(SCREENSHOTS_PATH)
        img_gray = img_color.convert("L")

        # Save grayscale image (overwrites the original)
        img_gray.save(SCREENSHOTS_PATH)
        print(f"Saved {SCREENSHOTS_PATH} in grayscale mode.")

        # Remove the file afterward
        os.remove(SCREENSHOTS_PATH)
        #print(f"Returning all 0's to caller. Please replace!")
        #return np.zeros(shape=(*GAME_RESOLUTION, 1))

    def read16(self, address:int) -> np.int16:
        print(f"Reading 16 bits from address {hex(address)}")
        return np.int16(0)

    def read8(self, address:int) -> np.int8:
        print(f"Reading 8 bits from address {hex(address)}")
        return np.int8(0)
    

