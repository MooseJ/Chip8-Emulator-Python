import pygame, sys
from pygame.locals import *

key_to_number = {
    pygame.K_x: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_q: 4,
    pygame.K_w: 5,
    pygame.K_e: 6,
    pygame.K_a: 7,
    pygame.K_s: 8,
    pygame.K_d: 9,
    pygame.K_z: 0xa,
    pygame.K_c: 0xb,
    pygame.K_4: 0xc,
    pygame.K_r: 0xd,
    pygame.K_f: 0xe,
    pygame.K_v: 0xf

}

class Chip8Input(object): 

    def __init__(self, pygame):
        self.pygame = pygame

    def handle_input(self, chip8):
        for event in pygame.event.get():
            if event.type == QUIT or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == event.key == K_SPACE:
                chip8.reset()
            if event.type == pygame.KEYDOWN and event.key in key_to_number:
                chip8.keys[key_to_number[event.key]] = 1
            if event.type == pygame.KEYUP and event.key in key_to_number:
                chip8.keys[key_to_number[event.key]] = 0
    