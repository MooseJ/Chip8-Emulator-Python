from chip8.chip8 import Chip8
from chip8.display import Chip8Display
from chip8.input import Chip8Input
from chip8.sound import Chip8Sound


import pygame
import sys
import time

if len(sys.argv) != 2:
    print("Invalid command!")
    print("Should be python <Name Of Game>!")
    exit()


pygame.init()
Display = Chip8Display(pygame)
Input = Chip8Input(pygame)
Sound = Chip8Sound(pygame)


Chip = Chip8(sys.argv[1])

while True:
    Input.handle_input(Chip)
    Sound.play(Chip)
    Chip.perform_cycle()
    Display.draw(Chip)
    #emulate 60HZ speed of processor 
    time.sleep(.0012)
