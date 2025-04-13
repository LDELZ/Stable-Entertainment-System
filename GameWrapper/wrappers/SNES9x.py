import os
import socket
import subprocess
import sys
import threading
import time

import numpy as np
import pygetwindow as gw
import win32con
import win32gui
from PIL import Image, ImageGrab
from pynput.keyboard import Controller, Key

from GameWrapper.wrappers.WrapperInterface import WrapperInterface

# Set the current directory as the script execution directory
SCRIPT_DIR = os.path.curdir #os.path.dirname(os.path.abspath(__file__))
#os.chdir(SCRIPT_DIR)

# Paths
SNES9X_EXE = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/snes9x.exe"))
ROM_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Roms/smw_patched.sfc"))
SCREENSHOTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Screenshots"))
SCREENSHOTS_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Screenshots/smw000.png"))
SAVESTATE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Saves/smw_patched.000"))
LUASCRIPT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "lua_server.lua"))
WINDOW_TITLE = "Snes9x rerecording 1.51 v7.1"
HOST = '127.0.0.1'
PORT = 12345

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
    def __init__(self, disable_keys:bool = False):
        super().__init__()
        self.disable_keys = disable_keys
        self.is_ready = False
        self.keyboard = Controller()
        self.process = None
        self.n = 5
        self.keymapping = KEYMAP
        self.held_keys = set()
        self.ram_map:dict[int:int] = {}
        self.ram_mutex = threading.Lock()
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(100)

    def send_command(self, command:str):
        self.socket.send(f"{command}\n".encode())
        self.socket.recv(1000) #Wait for an ok

    def pressButton(self, button):
        if not self.disable_keys:
            key = KEYMAP.get(button, button)
            self.keyboard.press(key)
            time.sleep(1)
            self.keyboard.release(key)
    
    def connect_lua_socket(self, host=HOST, port=PORT):
        """Connect to the lua server"""
        print("Connecting to server...")
        self.socket.connect((HOST, PORT))
        print("Connected!")

    def focus_snes9x(self):
        for window in gw.getWindowsWithTitle("snes9x"):
            win32gui.ShowWindow(window._hWnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(window._hWnd)
            print("SNES9x window focused.")
            return
        print("SNES9x window not found.")
    
    def launchEmulator(self):
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        init_script = os.path.join(parent_dir, "emulator_initialize.py")
        subprocess.run([sys.executable, init_script], check=True)

    def startGame(self):
        """
        Navigates the emulator to load the game and take the initial savestate. Sets up any lua scripts
        """
        print("Starting Game!")
        #TEMP enable keypresses

        # Ensure the ROM file still exists in the Roms folder
        if not os.path.exists(ROM_PATH):
            raise FileNotFoundError(f"ROM not found at: {ROM_PATH}")

        for filename in os.listdir(SCREENSHOTS_DIR):
            file_path = os.path.join(SCREENSHOTS_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Open the emulator with the SMW ROM
        subprocess.Popen([SNES9X_EXE, ROM_PATH])
        self.wait_for_windows("Snes9x rerecording")
        self.focus_snes9x()

        # Disable the background and the in-frame counter
        self.pressButton('2')
        self.pressButton('.')
        self.pressButton(Key.backspace)
        self.wait_for_windows("Lua Script")
        self.focus_snes9x()

        # This was originally used for listening for RAM data but this will be changing soon. Possibly remove
        self.connect_lua_socket()
        #threading.Thread(target=self.listen_for_ram_data, daemon=True).start()

        if not os.path.exists(SAVESTATE_PATH):
            print("No savestate found! Creating new Level 1 savestate.")
            # Get the level 1 savestate
            time.sleep(5)
            for _ in range(4):
                self.pressButton(Key.space)
                time.sleep(0.5)
            time.sleep(4)
            self.saveState("smw.000")
        else:
            print("Savestate found! Loading current savestate")
            self.loadState("smw.000")

        # Start Movie
        # self.pressButton("m")
        # time.sleep(0.5)
        # self.pressButton(Key.enter)

        self.is_ready = True

    def sendButtons(self, key_list:list[str]):
        """
        Sends the buttons to the emulator. Any button not pushed should be released
        """
        print(f"Sending {key_list}")
        self.send_command("press;" + "".join(key_list))

    def releaseAllButtons(self):
        self.sendButtons([])

    def advance(self, n:int):
        """
        Advances the emulator by n frames
        """
        self.send_command(f"adv; {n}")

    def loadState(self, state_name:str):
        """
        Make the emulator load some system state called state_name
        """
        print(f"Loading save state {state_name}...")
        self.send_command("load_save;")

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



    def screenshot(self) -> np.ndarray:
        """
        Capture a pixel-perfect SNES frame, save it as a file, and return as a NumPy array.
        """
        WINDOW_TITLE = "Snes9x"
        windows = gw.getWindowsWithTitle(WINDOW_TITLE)
        if not windows:
            raise RuntimeError(f"No window found with title containing '{WINDOW_TITLE}'")

        self.refocus_game()
        win = windows[0]

        # Grab full window
        bbox = (win.left, win.top, win.right, win.bottom)
        img = ImageGrab.grab(bbox=bbox).convert("L")

        # Crop borders
        trim_top = 70
        trim_bottom = 20
        trim_left = 8
        trim_right = 8
        img_cropped = img.crop((
            trim_left,
            trim_top,
            img.width - trim_right,
            img.height - trim_bottom
        ))

        img_resized = img_cropped.resize((256, 224), Image.NEAREST)

        # Save a sample image; currently removed. Uncomment for debugging
        img_resized.save(f"screenshot_test.png")

        return np.array(img_resized)

    def populate_mem(self) -> None:
        self.socket.send("send_mem;\n".encode())
        ret_str = self.socket.recv(2048).decode().strip()
        parts = ret_str.split(',')

        frame = None
        ram_parts = []

        # Lock the ram mutex

        for part in parts:
            if part.startswith("Frame="):
                frame = int(part.split("=")[1])
            else:
                ram_parts.append(part)

        with self.ram_mutex:
            self.ram_map.clear()
            for rampart in ram_parts:
                eq_sign = rampart.find("=")
                addr = rampart[0:eq_sign]
                val = rampart[eq_sign + 1:]
                self.ram_map[int(addr, 16)] = int(val, 10)

        return

    def readu16(self, address):
        #Read the upper and lower bytes
        lower = np.uint16(self.readu8(address))
        upper = np.uint16(self.readu8(address + 1))
        return (upper << 8) | lower
        #Aquire the ram_map lock

    def readu8(self, address: int) -> np.int8:
        with self.ram_mutex:
            if(address in self.ram_map.keys()):
                return np.uint8(self.ram_map[address])
            else:
                raise RuntimeError(f"Address {address:x} is not in the ram map!")

    def refocus_game(self):
        if self.disable_keys:
            return
        windows = gw.getWindowsWithTitle(WINDOW_TITLE)
        if not windows:
            raise RuntimeError(f"No window found with title containing '{WINDOW_TITLE}'")
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.2)

    def wait_for_windows(self, name:str):
        while len(gw.getWindowsWithTitle(name)) == 0:
            time.sleep(0.2)
        print(f"Found {name}!")