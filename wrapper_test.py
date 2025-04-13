import os
import sys
import numpy as np
from GameWrapper.wrappers.WrapperInterface import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SNES9x import SNES9x

def main():
    emulator = SNES9x()
    emulator.startGame()
    while(True):
        emulator.advance(1)
        emulator.populate_mem()
        x_pos = np.uint16(emulator.readu16(X_ADDR))
        y_pos = np.uint16(emulator.readu16(Y_ADDR))
        x_vel = np.int8(emulator.readu8(X_VEL))
        y_vel = np.int8(emulator.readu8(Y_VEL))
        print(f"Pos: {x_pos}, {y_pos}")
        print(f"Val: {x_vel}, {y_vel}")
        hit_piece = emulator.readu8(END_LVL_TIMER)
        print(hit_piece)
        if(hit_piece == PLAYER_PIECE):
            print("Piece!")

if __name__ == '__main__':
    main()