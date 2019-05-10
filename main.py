from chip8 import Chip8
import pygame, sys
from pygame.locals import *
import time

chip = Chip8()
chip.load_rom('UFO')
chip.initialize()

pygame.init()
size = (640, 320)

width = size[0]
height = size[1]

black = (148, 150, 126)

screen = pygame.display.set_mode(size, DOUBLEBUF)
screen.fill(black)

def draw():
    # print(chip.display)
    # print(numpy.reshape(chip.display, (32, 64)))
    for row in range(32):
        for col in range(64):
            display_index = row * 64 + col
            draw = chip.display[display_index]
            color = None
            if draw == 1: 
                color = (1, 3, 17)
            else:
                color = (148, 150, 126)
            pygame.draw.rect(screen, color, (col*10, row*10, 9, 9))

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

effect = pygame.mixer.Sound('buzz.wav')


while True:

    #input
    for event in pygame.event.get():
        if event.type == QUIT or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key in key_to_number:
            chip.keys[key_to_number[event.key]] = 1
            print(chip.keys)
        if event.type == pygame.KEYUP and event.key in key_to_number:
            chip.keys[key_to_number[event.key]] = 0

    if chip.ST == 1:
        effect.play()
    #cpu
    chip.perform_cycle()



    #output
    if chip.draw_flag:
        chip.draw_flag = False
        draw()
        pygame.display.update()
    
    time.sleep(.0012)
