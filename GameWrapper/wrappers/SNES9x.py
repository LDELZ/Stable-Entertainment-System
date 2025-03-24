import os
from pynput.keyboard import Controller, Key
import time
import subprocess
from PIL import ImageGrab
import numpy as np
import pygetwindow as gw
import win32gui
import win32con
from GameWrapper.wrappers.WrapperInterface import WrapperInterface
import socket
import pyautogui

# Set the current directory as the script execution directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Paths
SNES9X_EXE = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/snes9x.exe"))
ROM_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Roms/smw.sfc"))
SCREENSHOTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Screenshots"))
SCREENSHOTS_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Screenshots/smw000.png"))
SAVESTATE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../snes9x/Saves/smw.000"))
LUASCRIPT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../memory_server.lua"))
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
    def __init__(self):
        self.is_ready = False
        self.keyboard = Controller()
        self.process = None
        self.n = 5
        self.keymapping = KEYMAP
        self.held_keys = set()

    def pressButton(self, button):
        key = KEYMAP.get(button, button)
        self.keyboard.press(key)
        time.sleep(0.1)
        self.keyboard.release(key)
    
    def connect_lua_socket(self, host=HOST, port=PORT):
        """Starts a TCP server and waits for a Lua socket connection"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        print(f"[Socket] Listening on {host}:{port}...")

        conn, addr = s.accept()
        print(f"[Socket] Connected by {addr}")
        self.conn = conn

    def focus_snes9x(self):
            for window in gw.getWindowsWithTitle("snes9x"):
                win32gui.ShowWindow(window._hWnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(window._hWnd)
                print("SNES9x window focused.")
                return
            print("SNES9x window not found.")
    
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
        time.sleep(1)
        self.focus_snes9x()
        self.pressButton(Key.backspace)
        self.focus_snes9x()

        #Remove the background layer
        time.sleep(1)
        self.pressButton('2')

        self.connect_lua_socket()

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
        self.is_ready = True
            
    def sendButtons(self, key_list:list[str]):
        """
        Sends the buttons to the emulator. Any button not pushed should be released
        """
        active = set(key_list)

        for logical_btn, physical_key in self.keymapping.items():
            if logical_btn in active and physical_key not in self.held_keys:
                self.keyboard.press(physical_key)
                self.held_keys.add(physical_key)
            elif logical_btn not in active and physical_key in self.held_keys:
                self.keyboard.release(physical_key)
                self.held_keys.remove(physical_key)

    def releaseAllButtons(self):
        self.sendButtons([])

    def advance(self, n:int):
        """
        Advances the emulator by n frames
        """
        time.sleep(0.1)
        for _ in range(n):
            self.pressButton("\\")

    def loadState(self, state_name:str):
        """
        Make the emulator load some system state called state_name
        """
        self.pressButton(Key.f1)
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

    def screenshot(self) -> np.ndarray:
        """
        Take a screenshot. (Convert to grayscale) and return as an np.array
        """
        windows = gw.getWindowsWithTitle(WINDOW_TITLE)
        if not windows:
            raise RuntimeError(f"No window found with title containing '{WINDOW_TITLE}'")

        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.5)

        bbox = (win.left, win.top, win.right, win.bottom)
        img_gray = ImageGrab.grab(bbox=bbox).convert("L")
        return np.array(img_gray)
    
    def read_ram16(self, address):
        if not self.conn:
            raise RuntimeError("Lua socket not connected")

        self.conn.sendall(f'READ16,{hex(address)}\n'.encode())
        self.advance(1)  # ← let Lua have a chance to run
        response = self.conn.recv(1024).decode().strip()

        if response.startswith("VALUE"):
            return int(response.split(",")[1])
        return None



    def read8(self, address:int) -> np.int8:
        print(f"Reading 8 bits from address {hex(address)}")
        return np.int8(0)