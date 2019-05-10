import pygame, sys
from pygame.locals import *

class Chip8Sound(object):
    def __init__(self, pygame):
        self.pygame = pygame
        self.effect = pygame.mixer.Sound('buzz.wav')
    

    def play(self, chip8):
        if chip8.ST == 1:
            self.effect.play()
