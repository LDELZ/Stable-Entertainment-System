'''
******************************************************************************
 * File:        SNES9x.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: This program enables control of the SNES9x emulator using
                pynput commands to simulate keyboard presses. It is required
                for receiving memory values, taking screenshots, and passing
                inputs directly from python. Inputs are handled by Lua for
                actual gameplay processing, but the functions here enable
                broader emulator control to simulate external commands.
 * Usage:       This program is automatically used by the GameWrapper class
                and is not intended for use on its own.
 ******************************************************************************
 '''

# Imports
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
SCRIPT_DIR = os.path.curdir

# Define the paths for the savestates, lua scripts, roms, emulator executables, and TCP ports
SNES9X_EXE = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/snes9x.exe"))
ROM_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Roms/smw_patched.sfc"))
SCREENSHOTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Screenshots"))
SCREENSHOTS_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Screenshots/smw000.png"))
SAVESTATE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "snes9x/Saves/smw_patched.000"))
LUASCRIPT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "lua_server.lua"))
WINDOW_TITLE = "Snes9x rerecording 1.51 v7.1"
HOST = '127.0.0.1'
PORT = 12345

# Define the keymap conversion from pynput keyboard presses to SNES controller inputs
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

'''
------------------------------------------------------------------------------
 * Class: SNES9x
 * --------------------
 * Description:
 *	Represents an instance of a SNES9x emulator control interface. Emulator status
    variables and basic control functions are specified here.
 '''
class SNES9x(WrapperInterface):

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x constructor
    * --------------------
    * Description:
    *	Initializes an instance of a SNES9x control interface by specifying
        the number of frames to advance, a simulated keyboard input controller
        the keys to hold, and whether the emulator is ready to advance.
    *
    * Arguments:   disable_keys, record_movie
    * Returns:     none
    '''
    def __init__(self, disable_keys:bool = False, record_movie:bool = False):
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
        self.record_movie = record_movie

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x send_command
    * --------------------
    * Description:
    *	Sends a command over the TCP socket and waits for a response
    *
    * Arguments:   The string command to send
    * Returns:     none
    '''
    def send_command(self, command:str):
        self.socket.send(f"{command}\n".encode())
        self.socket.recv(1000)

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x pressButton
    * --------------------
    * Description:
    *	Receives a keyboard input and presses the corresponding SNES9x button
        for 1 second. If the key is in the keymap, the keymapped button is pressed,
        otherwise the direct keyboard input is pressed. The timer prevents input
        ghosting from too quick of inputs being sent to the emulator.
    *
    * Arguments:   The button to press
    * Returns:     none
    '''
    def pressButton(self, button):

        # Check if the input is in the list of disabled keys
        if not self.disable_keys:

            # Convert the input to the keymap conversion
            key = KEYMAP.get(button, button)

            # Press the button for 1 second and then release
            self.keyboard.press(key)
            time.sleep(1)
            self.keyboard.release(key)
    
    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x connect_lua_socket
    * --------------------
    * Description:
    *	Connects to the LuaSocket server over the TCP connection specified by the
        HOST and PORT constants.
    *
    * Arguments:   The host and port of the Lua server
    * Returns:     none
    '''
    def connect_lua_socket(self, host=HOST, port=PORT):
        print("Connecting to server...")
        self.socket.connect((HOST, PORT))
        print("Connected!")

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x focus_snes9x
    * --------------------
    * Description:
    *	Brings the SNES9x window into the main focus in the windows environment.
        This is required because opening other programs and certain keyboard commands
        bring other programs into focus, which pauses the emulator.
    *
    * Arguments:   none
    * Returns:     none
    '''
    def focus_snes9x(self):
        for window in gw.getWindowsWithTitle("snes9x"):
            win32gui.ShowWindow(window._hWnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(window._hWnd)
            print("SNES9x window focused.")
            return
        print("SNES9x window not found.")
    
    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x launchEmulator
    * --------------------
    * Description:
    *	Launches the SNES9x emulator as a subprocess from the Python execution
    *
    * Arguments:   none
    * Returns:     none
    '''
    def launchEmulator(self):
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        init_script = os.path.join(parent_dir, "emulator_initialize.py")
        subprocess.run([sys.executable, init_script], check=True)

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x startGame
    * --------------------
    * Description:
    *	Navigates the emulator to load the game and take the initial savestate. 
        Sets up the required lua scripts to be used after initialization. This
        is required foro loading the lua script using emulator Hotkeys
    *
    * Arguments:   none
    * Returns:     none
    '''
    def startGame(self):

        # Ensure the ROM file still exists in the Roms folder
        if not os.path.exists(ROM_PATH):
            raise FileNotFoundError(f"ROM not found at: {ROM_PATH}")

        # Purge the screenshots folder if any screenshots exist
        for filename in os.listdir(SCREENSHOTS_DIR):
            file_path = os.path.join(SCREENSHOTS_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Open the emulator with the SMW ROM
        subprocess.Popen([SNES9X_EXE, ROM_PATH])
        self.wait_for_windows("Snes9x rerecording")
        self.focus_snes9x()

        # Disable the background and the in-frame counter
        # This is required so that the model does not use emulator memory values to learn
        self.pressButton('2')
        self.pressButton('.')
        self.pressButton(Key.backspace)
        self.wait_for_windows("Lua Script")
        self.focus_snes9x()

        # Connect to the Lua Socket
        self.connect_lua_socket()

        # Check if a savestate is found to revert to; if not, automate creating one
        if not os.path.exists(SAVESTATE_PATH):
            print("No savestate found! Creating new Level 1 savestate.")
            
            # Get the level 1 savestate (requires going through intro prompts)
            time.sleep(5)
            for _ in range(4):
                self.pressButton(Key.space)
                time.sleep(0.5)
            time.sleep(4)
            self.saveState("smw.000")

        # The savestate was found, so simply load it
        else:
            print("Savestate found! Loading current savestate")
            self.loadState("smw.000")

        # Start a SNES9x movie recording
        if self.record_movie:
            self.pressButton("m")
            time.sleep(0.5)
            self.pressButton(Key.enter)

        # Set the emulator ready flag to true
        self.is_ready = True

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x sendButtons
    * --------------------
    * Description:
    *	Sends the buttons to the emulator. Any button not pushed should be released
    *
    * Arguments:   The list of buttons to push
    * Returns:     none
    '''
    def sendButtons(self, key_list:list[str]):
        print(f"Sending {key_list}")
        self.send_command("press;" + "".join(key_list))

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x releaseAllButtons
    * --------------------
    * Description:
    *	Sends a blank button list of buttons to push. This results in all of 
        the buttons being released
    *
    * Arguments:   none
    * Returns:     none
    '''
    def releaseAllButtons(self):
        self.sendButtons([])

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x advance
    * --------------------
    * Description:
    *	Advances the emulator by n frames in frame advance mode
    *
    * Arguments:   none
    * Returns:     none
    '''
    def advance(self, n:int):
        self.send_command(f"adv; {n}")

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x loadState
    * --------------------
    * Description:
    *	Loads the save state created during save_state
    *
    * Arguments:   The save state file name
    * Returns:     none
    '''
    def loadState(self, state_name:str):
        print(f"Loading save state {state_name}...")
        self.send_command("load_save;")

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x saveState
    * --------------------
    * Description:
    *	Saves a current game state from the emulator
    *
    * Arguments:   The save state file name
    * Returns:     none
    '''
    def saveState(self, state_name:str):
        self.keyboard.press(Key.shift)
        self.keyboard.press(Key.f1)
        time.sleep(0.1)
        self.keyboard.release(Key.f1)
        self.keyboard.release(Key.shift)
        print(f"Saving state to {state_name}...")


    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x screenshot
    * --------------------
    * Description:
    *	Captures a pixel-perfect SNES frame, saves it as a file, and return as a NumPy array.
        Captures a screenshot of the current game window and converts it to a numpy
        array of grayscale values representing the image. This is used to pass back
        to the SB3 environment.
    *
    * Arguments:   none
    * Returns:     An np array of grayscale image data
    '''
    def screenshot(self) -> np.ndarray:

        # Focus the SNES9x instance window
        WINDOW_TITLE = "Snes9x"
        windows = gw.getWindowsWithTitle(WINDOW_TITLE)
        if not windows:
            raise RuntimeError(f"No window found with title containing '{WINDOW_TITLE}'")
        self.refocus_game()
        win = windows[0]

        # Capture the game window; cropping is used to remove the window header
        # Convert the image to grayscale
        bbox = (win.left, win.top, win.right, win.bottom)
        img = ImageGrab.grab(bbox=bbox).convert("L")
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

        # Resize the image to be pixel-perfect for the original SNES hardware
        # This imporves conversion efficiency but also simulates human-level play
        img_resized = img_cropped.resize((256, 224), Image.NEAREST)

        # Save a sample image; currently removed. Uncomment for debugging
        # img_resized.save(f"screenshot_test.png")

        # Return the matrix of grayscale values representing the image
        return np.array(img_resized)

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x populate_mem
    * --------------------
    * Description:
    *	Retrieves and updated memory values from the emulator RAM mapping
    *
    * Arguments:   none
    * Returns:     none
    '''
    def populate_mem(self) -> None:

        # Obtain the raw memory values
        self.socket.send("send_mem;\n".encode())
        ret_str = self.socket.recv(2048).decode().strip()
        parts = ret_str.split(',')
        frame = None
        ram_parts = []

        # Lock the ram mutex; this is used to prevent memory read/overwrite race conditions
        for part in parts:
            if part.startswith("Frame="):
                frame = int(part.split("=")[1])
            else:
                ram_parts.append(part)

        # Clear the current ram values and replace them with the captured raw values
        with self.ram_mutex:
            self.ram_map.clear()
            for rampart in ram_parts:
                eq_sign = rampart.find("=")
                addr = rampart[0:eq_sign]
                val = rampart[eq_sign + 1:]
                self.ram_map[int(addr, 16)] = int(val, 10)
        return

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x readu16
    * --------------------
    * Description:
    *	Reads a 16-bit ram address value from the Lua memory values captured from
        in-game. 16-bit and 8-bit memory values are required to capture the full
        behavior of the instances in the game
    *
    * Arguments:   none
    * Returns:     none
    '''
    def readu16(self, address):
        #Read the upper and lower bytes
        lower = np.uint16(self.readu8(address))
        upper = np.uint16(self.readu8(address + 1))
        return (upper << 8) | lower
        #Aquire the ram_map lock

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x readu8
    * --------------------
    * Description:
    *	Reads an 8-bit ram address value from the Lua memory values captured from
        in-game. 16-bit and 8-bit memory values are required to capture the full
        behavior of the instances in the game
    *
    * Arguments:   none
    * Returns:     none
    '''
    def readu8(self, address: int) -> np.int8:
        with self.ram_mutex:
            if(address in self.ram_map.keys()):
                return np.uint8(self.ram_map[address])
            else:
                return np.uint8(0)

    '''
    ------------------------------------------------------------------------------
    * Function: SNES9x refocus_game
    * --------------------
    * Description:
    *	Brings the SNES9x window into the main focus in the windows environment.
        This is required because opening other programs and certain keyboard commands
        bring other programs into focus, which pauses the emulator.
    *
    * Arguments:   none
    * Returns:     none
    '''
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

        '''
    ------------------------------------------------------------------------------
    * Function: SNES9x wait_for_windows
    * --------------------
    * Description:
    *	Waits a small amount of time to prevent Windows command overloading, which
        can result in timing issues where commands are missed between interfaces.
    *
    * Arguments:   The name of the program to wait on
    * Returns:     none
    '''
    def wait_for_windows(self, name:str):
        while len(gw.getWindowsWithTitle(name)) == 0:
            time.sleep(0.2)
        print(f"Found {name}!")