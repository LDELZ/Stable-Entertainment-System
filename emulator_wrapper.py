import os
from pynput.keyboard import Controller, Key
import time
import subprocess
from PIL import Image
import keyboard

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACT_FOLDER = "snes9x"
os.chdir(SCRIPT_DIR)
EXTRACT_PATH = os.path.join(SCRIPT_DIR, EXTRACT_FOLDER)
SNES9X_EXE = os.path.join(EXTRACT_PATH, "snes9x.exe")
ROM_PATH = os.path.join(SCRIPT_DIR, "snes9x/Roms/smw.sfc")
LUA_SCRIPT = os.path.join(SCRIPT_DIR, "bot.lua")
ROMS_FOLDER = os.path.join(EXTRACT_PATH, "Roms")
COLOR_IMAGE_PATH = "snes9x/Screenshots/smw000.png"
NUM_FRAMES = 5
COLOR_IMAGE_PATH = "snes9x/Screenshots/smw000.png"
KEYBOARD = Controller()
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

def process_inputs():
    """Function to process inputs when Right Ctrl is pressed."""
    print("Right Ctrl detected! Processing inputs...")

    # Process and send inputs
    inputs = ['A', 'B', 'X']
    press_input_list(inputs)

    # Check and delete image if it exists
    if os.path.exists(COLOR_IMAGE_PATH):
        os.remove(COLOR_IMAGE_PATH)

    # Advance n frames
    for _ in range(NUM_FRAMES):
        press_and_release("\\")

    # Capture screenshot & convert to grayscale
    press_and_release(Key.f12)
    time.sleep(0.1)
    convert_grayscale()


def press_input_list(inputs):
    """Press and release each key in the given list based on KEYMAP."""
    for key in inputs:
        mapped_key = KEYMAP[key]
        print(f"Pressing: {mapped_key}")

        # Press and release the key
        KEYBOARD.press(mapped_key)

def release_all_inputs():
    for key in KEYMAP:
        KEYBOARD.release(key)

def convert_grayscale():
    # Ensure the color image exists before processing
    if not os.path.exists(COLOR_IMAGE_PATH):
        print(f"Warning: Color image not found at {COLOR_IMAGE_PATH}")
        return

    # Load the original image
    image = Image.open(COLOR_IMAGE_PATH)

    # Convert to grayscale
    gray_image = image.convert("L")

    # Overwrite the original file with the grayscale version
    gray_image.save(COLOR_IMAGE_PATH)  # Saves over the color image

    print(f"Replaced {COLOR_IMAGE_PATH} with its grayscale version")

def press_and_release(button):
    KEYBOARD.press(button)
    time.sleep(0.1)
    KEYBOARD.release(button)

if __name__ == "__main__":
    main()
    