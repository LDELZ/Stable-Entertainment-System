
class Button():
    def __init__(self, name:str, keycode:int = 0):
        self.name:str = name
        self.keycode = keycode

    def __str__(self):
        return self.name



#Directions
BUTTON_UP = Button("Up")
BUTTON_DOWN = Button("Down")
BUTTON_LEFT = Button("Left")
BUTTON_RIGHT =  Button("Right")

BUTTON_A = Button("A")
BUTTON_B = Button("B")
BUTTON_X = Button("X")
BUTTON_Y = Button("Y")
BUTTON_L = Button("L")
BUTTON_R = Button("R")

BUTTON_SELECT =  Button("Select")
BUTTON_START =  Button("Start")

ALL_BUTTONS = (BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y, BUTTON_L, BUTTON_R, BUTTON_SELECT, BUTTON_START)