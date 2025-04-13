import os
import sys
import time

from PIL import Image
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SNES9x import SNES9x

def main():
    emulator = SNES9x()
    emulator.startGame()
    while(True):
        emulator.advance(1)
        emulator.populate_mem()
        print(emulator.read16(0x7E00D1))

if __name__ == '__main__':
    main()