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
import threading
import sys

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

    def pressButton(self, button):
        if not self.disable_keys:
            key = KEYMAP.get(button, button)
            self.keyboard.press(key)
            if self.is_ready:
                time.sleep(0.1)
            else:
                time.sleep(0.001)
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
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        # Path to emulator_initialize.py
        init_script = os.path.join(parent_dir, "emulator_initialize.py")

        # Run it with the same Python interpreter
        subprocess.run([sys.executable, init_script], check=True)

    def startGame(self):
        """
        Navigates the emulator to load the game and take the initial savestate. Sets up any lua scripts
        """
        print("Starting Game!")
        #TEMP enable keypresses
        save_disable = self.disable_keys
        self.disable_keys = False

        # Ensure the ROM file still exists in the Roms folder
        if not os.path.exists(ROM_PATH):
            raise FileNotFoundError(f"ROM not found at: {ROM_PATH}")

        for filename in os.listdir(SCREENSHOTS_DIR):
            file_path = os.path.join(SCREENSHOTS_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Open the emulator with the SMW ROM
        subprocess.Popen([SNES9X_EXE, ROM_PATH])
        time.sleep(5)
        self.focus_snes9x()
        time.sleep(5)
        self.pressButton(Key.backspace)
        time.sleep(5)
        self.focus_snes9x()

        #Remove the background layer
        time.sleep(1)
        self.pressButton('2')

        self.connect_lua_socket()
        # Start RAM listener in background
        threading.Thread(target=self.listen_for_ram_data, daemon=True).start()
        
        if not os.path.exists(SAVESTATE_PATH):
            print("No savestate found! Creating new Level 1 savestate.")
            # Get the level 1 savestate
            time.sleep(5)
            for _ in range(4):
                self.pressButton(Key.space)
                time.sleep(0.5)
            time.sleep(15)
            self.pressButton(Key.space)
            time.sleep(3)
            self.pressButton(Key.left)
            time.sleep(2)
            self.pressButton('A')
            time.sleep(3)
            self.saveState("smw.000")
        else:
            print("Savestate found! Loading current savestate")
            self.loadState("smw.000")

        # Start Movie
        self.pressButton("m")
        time.sleep(0.5)
        self.pressButton(Key.enter)

        # Enter frame-advance mode
        self.pressButton("\\")
        self.is_ready = True
        self.disable_keys = save_disable

    def sendButtons(self, key_list:list[str]):
        """
        Sends the buttons to the emulator. Any button not pushed should be released
        """
        if self.disable_keys:
            return
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

        self.refocus_game()

        win = windows[0]

        bbox = (win.left, win.top, win.right, win.bottom)
        img_gray = ImageGrab.grab(bbox=bbox).convert("L")
        return np.array(img_gray)
    

    def listen_for_ram_data(self):
        while True:
            try:
                self.conn.send("Ok\n".encode())
                data = self.conn.recv(1024)
                if not data:
                    break
                decoded = data.decode().strip()
                # Split into key=value parts
                parts = decoded.split(',')

                frame = None
                ram_parts = []

                # Lock the ram mutex

                for part in parts:
                    if part.startswith("Frame="):
                        frame = int(part.split("=")[1])
                    else:
                        ram_parts.append(part)  # already in addr=value format

                with self.ram_mutex:
                    self.ram_map.clear()
                    for rampart in ram_parts:
                        eq_sign = rampart.find("=")
                        addr = rampart[0:eq_sign]
                        val = rampart[eq_sign+1:]
                        self.ram_map[int(addr, 16)] = int(val, 10)


            except Exception as e:
                print(f"[ERROR] Failed to parse RAM data: {e}")
                #break

    def read16(self, address):
        #Read the upper and lower bytes
        lower = self.read8(address)
        upper = self.read8(address + 1)
        return np.uint16((upper << 8) | lower)
        #Aquire the ram_map lock

    def read8(self, address: int) -> np.int8:
        with self.ram_mutex:
            if(address in self.ram_map.keys()):
                return np.uint8(self.ram_map[address])
            else:
                print(f"Address {address:x} is not in the ram map!")
                return np.uint(0)

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
        time.sleep(0.5)

