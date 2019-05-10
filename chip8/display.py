import pygame
from pygame.locals import *

class Chip8Display(object):
    size = (640, 320)

    width = size[0]
    height = size[1]

    foreground = (1, 3, 17)
    background = (148, 150, 126)

    def __init__(self, pygame):
        self.pygame = pygame  
        self.screen = self.pygame.display.set_mode(self.size, DOUBLEBUF)
        self.screen.fill(self.background)

    def draw(self, chip8):
        if chip8.draw_flag:
            chip8.draw_flag = False
            for row in range(32):
                for col in range(64):
                    pixel_location = row * 64 + col
                    pixel = chip8.display[pixel_location]
                    pixel_color = self.foreground if pixel == 1 else self.background
                    self.pygame.draw.rect(self.screen, pixel_color, (col*10, row*10, 9, 9))
            self.pygame.display.update()