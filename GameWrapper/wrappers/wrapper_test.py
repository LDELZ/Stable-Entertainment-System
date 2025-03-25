import os
import sys
from PIL import Image
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SNES9x import SNES9x

def main():
    emulator = SNES9x()
    emulator.launchEmulator()
    emulator.startGame()

    input_sequence = [
        ["LEFT", "A"],
        ["UP", "Y", "RIGHT"],
        ["B"],
        ["RIGHT"],
        ["DOWN", "B"],
        ["A", "R", "RIGHT"],
        ["UP"],
        ["L", "R", "Y"],
        ["LEFT", "DOWN"],
        ["RIGHT"],
        ["UP", "X"],
        ["X", "A", "B"],
        ["LEFT"],
        ["DOWN"],
        ["RIGHT", "Y"],
        ["L"],
        ["A", "B"],
        ["RIGHT"],
        ["RIGHT"]
    ]

    for i, inputs in enumerate(input_sequence):
        print(f"Frame {i + 1}: Sending {inputs}")
        emulator.sendButtons(inputs)
        emulator.advance(emulator.n)
        emulator.releaseAllButtons()
        frame = emulator.screenshot()

def test_save_screenshot(np_array: np.ndarray, filename: str = "screenshot_debug.png") -> None:
    '''
    This function is used to save an image of the stored screenshot
    It can be used to make sure the emulator window was saved and the screenshot is grayscaled
    '''
    img = Image.fromarray(np_array)
    img.save(filename)
    print(f"Saved image to {filename}")

if __name__ == '__main__':
    main()