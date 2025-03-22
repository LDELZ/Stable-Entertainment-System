import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SNES9x import SNES9x

def main():
    test_startGame()

def test_startGame():
    print("Starting SMW")
    emulator = SNES9x()
    emulator.startGame()
    
if __name__ == '__main__':
    main()