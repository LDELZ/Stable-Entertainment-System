import os
import sys
from PIL import Image
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SNES9x import SNES9x

def main():
    emulator = SNES9x()
    emulator.startGame()

if __name__ == '__main__':
    main() 