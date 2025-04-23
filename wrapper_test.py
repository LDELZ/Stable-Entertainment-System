'''
******************************************************************************
 * File:        wrapper_test.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: Initializes an emulator instance and starts the game in that
                subprocess. For each frame, it gets the memory values from the 
                Lua interface in SNES9x and stores the memory values for
                Mario's x/y-position and x/y-velocity. It checks if the level
                has been completed and prints a message indicating if so. Note
                that this is used for debugging game memory reading and game
                termination only.
 * Usage:       Run this program in a Python 3.12.x or higher environment.
 ******************************************************************************
 '''

# Import the game wrapper
import numpy as np
from GameWrapper.wrappers.WrapperInterface import *
from GameWrapper.wrappers.SNES9x import SNES9x

'''
------------------------------------------------------------------------------
* Function: main
* --------------------
* Description:
*	Initializes an emulator instance and starts the game in that subprocess.
    For each frame, it gets the memory values from the Lua interface in SNES9x
    and stores the memory values for Mario's x/y-position and x/y-velocity.
    It checks if the level has been completed and prints a message indicating
    if so. Note that this is used for debugging game memory reading and game
    termination only.
*
* Arguments:   none
* Returns:     none
'''
def main():

    # Initialize emulator instance
    emulator = SNES9x()
    emulator.startGame()

    # For each frame while the game is running
    while(True):

        # Advance frames and get the new memory values
        emulator.advance(1)
        emulator.populate_mem()

        # Parse the memory values into Mario's position and velocity
        x_pos = np.uint16(emulator.readu16(X_ADDR))
        y_pos = np.uint16(emulator.readu16(Y_ADDR))
        x_vel = np.int8(emulator.readu8(X_VEL))
        y_vel = np.int8(emulator.readu8(Y_VEL))
        print(f"Pos: {x_pos}, {y_pos}")
        print(f"Val: {x_vel}, {y_vel}")

        # Determine if the end of the level was reached
        hit_piece = emulator.readu8(END_LVL_TIMER)
        print(hit_piece)

        # If reached, display that the end was reached
        # Note: This is used for debugging game termination when reaching the goal
        if(hit_piece == PLAYER_PIECE):
            print("Piece!")

        # Store the current screenshot of othe game window
        emulator.screenshot()

# Executes starting at main when the program is executed
if __name__ == '__main__':
    main()