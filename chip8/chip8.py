import random
import time

#CONSTANTS
FONTS = [ 
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]
FLAG_REGISTER  = 0xF
PROGRAM_START_LOCATION = 0x200

class Chip8(object):
    def __init__(self, rom_name):
        self.rom_name = rom_name
        self.initialize()
        self.load_rom()

    def perform_cycle(self):
        opcode = (self.memory[self.program_counter] << 8) | self.memory[self.program_counter+1]
        first_byte_of_opcode = (opcode & 0xf000) >> 12
        instruction_map[first_byte_of_opcode](self, opcode)
        self.update_timers()
    
    def update_timers(self):
        if self.DT > 0:
            self.DT -= 1
        if self.ST > 0:
            self.ST -= 1
        

    def load_rom(self):
        file = open(self.rom_name, 'rb').read()
        i = 0
        while i < len(file):
            self.memory[i + PROGRAM_START_LOCATION] = file[i]
            i += 1

    def initialize(self):
        self.program_counter = PROGRAM_START_LOCATION
        self.memory = [0]*4096 #4kb of memory, 4096 bytes
        self.registers = [0]*16 #general purpose registers, 8 bit. 1byte

        self.I = 0
        self.ST = 0
        self.DT = 0

        self.stack_pointer = 0
        self.stack = []

        self.draw_flag = False #not actually a part of the chip, but helps with performance
        self.display = [0] * 64 * 32 # monochrome 64 by 32 pixel display

        self.keys = [0] * 16

        self.load_fonts()
    
    def load_fonts(self):
        for i in range(80):
            self.memory[i] = FONTS[i]
        

    def reset(self):
        self.initialize()
        self.load_rom()


#INSTRUCTIONS
def _0(chip8: Chip8, opcode): 
    """
    runs either _0nnn, _00E0, or _00EE
    """
    if opcode == 0x00E0:
        _00E0(chip8)
    elif opcode == 0x00EE:
        _00EE(chip8)
    else:
        _0nnn(chip8, opcode)

def _0nnn(chip8: Chip8, opcode):
    """ 
    SYS addr
    
    Jump to machine code routine at nnn

    nnn = a 12 bit value/addr
    """
    chip8.program_counter = get_nnn(opcode)

def _00E0(chip8: Chip8):
    """
    CLS

    Clear the display
    """
    chip8.display = [0] * 64 * 32
    chip8.program_counter += 2

def _00EE(chip8: Chip8):
    """
    RET

    Return from a subroutine

    The interpreter sets the program counter to the address at the top of the stack,
    then subtracts 1 from the stack pointer
    """
    chip8.program_counter = chip8.stack.pop()
    chip8.stack_pointer -= 1
    chip8.program_counter += 2

def _1nnn(chip8: Chip8, opcode):
    """
    JP addr

    Jump to location nnn

    The interpreter sets the program counter to nnn
    """
    chip8.program_counter = get_nnn(opcode)

def _2nnn(chip8: Chip8, opcode):
    """
    CALL addr

    Call subroutine at nnn

    The interpreter increments the stack pointer, 
    then puts the current PC on the top of the stack. 
    The PC is then set to nnn.
    """
    chip8.stack_pointer += 1
    chip8.stack.append(chip8.program_counter)
    chip8.program_counter = get_nnn(opcode)

def _3xkk(chip8: Chip8, opcode):
    """
    SE Vx, byte

    Skip next opcode if Vx = kk

    The interpreter compares register Vx to kk, 
    and if they are equal, 
    increments the program counter by 2.
    """
    VX_value = chip8.registers[get_Vx(opcode)]
    kk = get_kk(opcode)
    
    if chip8.registers[get_Vx(opcode)] == get_kk(opcode):
        chip8.program_counter += 4
    else:
        chip8.program_counter += 2

def _4xkk(chip8: Chip8, opcode):
    """
    SNE Vx, byte

    Skip next opcode if Vx != kk

    The interpreter compares register Vx to kk, 
    and if they are not equal, 
    increments the program counter by 2.
    """
    if chip8.registers[get_Vx(opcode)] != get_kk(opcode):
        chip8.program_counter += 4
    else:
        chip8.program_counter += 2
    

def _5xy0(chip8: Chip8, opcode):
    """
    SE Vx, Vy

    Skip next opcode if Vx = Vy.

    The interpreter compares register Vx to register Vy, 
    and if they are equal, 
    increments the program counter by 2.
    """
    if chip8.registers[get_Vx(opcode)] == chip8.registers[get_Vy(opcode)]:
        chip8.program_counter += 4
    else:
        chip8.program_counter += 2

def _6xkk(chip8: Chip8, opcode):
    """
    LD Vx, byte
    
    Set Vx = kk.
    
    The interpreter puts the value kk into register Vx.
    """
    chip8.registers[get_Vx(opcode)] = get_kk(opcode)
    chip8.program_counter += 2

def _7xkk(chip8: Chip8, opcode):
    """
    ADD Vx, byte

    Set Vx = Vx + kk.

    Adds the value kk to the value of register Vx, 
    then stores the result in Vx. 
    """
    chip8.registers[get_Vx(opcode)] += get_kk(opcode)
    chip8.program_counter += 2

def _8(chip8: Chip8, opcode):
    _8_instructions_map = {
        0x0: _8xy0,
        0x1: _8xy1,
        0x2: _8xy2,
        0x3: _8xy3,
        0x4: _8xy4,
        0x5: _8xy5,
        0x6: _8xy6,
        0x7: _8xy7,
        0xE: _8xyE
    }
    _8_instructions_map[get_n(opcode)](chip8, opcode)
    chip8.program_counter += 2

def _8xy0(chip8: Chip8, opcode):
    """
    LD Vx, Vy

    Set Vx = Vy.

    Stores the value of register Vy in register Vx.
    """
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    chip8.registers[get_Vx(opcode)] = Vy_register_value

def _8xy1(chip8: Chip8, opcode):
    """
    OR Vx, Vy

    Set Vx = Vx OR Vy

    Performs a bitwise OR on the values of Vx and Vy, 
    then stores the result in Vx. 
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    chip8.registers[get_Vx(opcode)] = Vx_register_value | Vy_register_value

def _8xy2(chip8: Chip8, opcode):
    """
    AND Vx, Vy

    Set Vx = Vx AND Vy.

    Performs a bitwise AND on the values of Vx and Vy, 
    then stores the result in Vx. 
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    chip8.registers[get_Vx(opcode)] = Vx_register_value & Vy_register_value

def _8xy3(chip8: Chip8, opcode):
    """
    XOR Vx, Vy

    Set Vx = Vx XOR Vy.

    Performs a bitwise exclusive OR on the values of Vx and Vy, 
    then stores the result in Vx. 
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    chip8.registers[get_Vx(opcode)] = Vx_register_value ^ Vy_register_value

def _8xy4(chip8: Chip8, opcode):
    """
    ADD Vx, Vy

    Set Vx = Vx + Vy, set VF = carry.

    The values of Vx and Vy are added together. 
    If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, 
    otherwise 0. 
    Only the lowest 8 bits of the result are kept, 
    and stored in Vx.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    registers_sum = Vx_register_value + Vy_register_value
    chip8.registers[get_Vx(opcode)] = registers_sum & 0xFF

    if registers_sum > 255:
        chip8.registers[FLAG_REGISTER] = 1



def _8xy5(chip8: Chip8, opcode):
    """
    SUB Vx, Vy

    Set Vx = Vx - Vy, set VF = NOT borrow.

    If Vx > Vy, 
    then VF is set to 1, 
    otherwise 0. 
    Then Vy is subtracted from Vx, 
    and the results stored in Vx.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    registers_difference = 0

    if Vx_register_value > Vy_register_value:
        chip8.registers[FLAG_REGISTER] = 1
        registers_difference = Vx_register_value - Vy_register_value
    else: 
        chip8.registers[FLAG_REGISTER] = 0
        registers_difference = Vy_register_value - Vx_register_value

    chip8.registers[get_Vx(opcode)] = registers_difference

def _8xy6(chip8: Chip8, opcode):
    """
    SHR Vx {, Vy}

    Set Vx = Vx SHR 1.

    If the least-significant bit of Vx is 1, 
    then VF is set to 1, 
    otherwise 0. 
    Then Vx is divided by 2.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]

    if (Vx_register_value & 0x1) == 1:
        chip8.registers[FLAG_REGISTER] = 1
    else: 
        chip8.registers[FLAG_REGISTER] = 0

    
    chip8.registers[get_Vx(opcode)] = Vx_register_value // 2 

    

def _8xy7(chip8: Chip8, opcode):
    """
    SUBN Vx, Vy

    Set Vx = Vy - Vx, set VF = NOT borrow.

    If Vy > Vx, 
    then VF is set to 1, 
    otherwise 0. 
    Then Vx is subtracted from Vy,
    and the results stored in Vx.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]

    registers_difference = 0

    if Vy_register_value > Vx_register_value:
        chip8.registers[FLAG_REGISTER] = 1
        registers_difference = Vy_register_value - Vx_register_value
    else: 
        chip8.registers[FLAG_REGISTER] = 0
        registers_difference = Vx_register_value - Vy_register_value

    chip8.registers[get_Vx(opcode)] = registers_difference

def _8xyE(chip8: Chip8, opcode):
    """
    SHL Vx {, Vy}

    Set Vx = Vx SHL 1.

    If the most-significant bit of Vx is 1, 
    then VF is set to 1, 
    otherwise to 0. 
    Then Vx is multiplied by 2.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]

    if ((Vx_register_value & 0x8) >> 3) == 1:
        chip8.registers[FLAG_REGISTER] = 1
    else: 
        chip8.registers[FLAG_REGISTER] = 0

    
    chip8.registers[get_Vx(opcode)] = Vx_register_value * 2 

def _9xy0(chip8: Chip8, opcode):
    """
    SNE Vx, Vy

    Skip next opcode if Vx != Vy.

    The values of Vx and Vy are compared, 
    and if they are not equal, 
    the program counter is increased by 2.
    """
    if chip8.registers[get_Vx(opcode)] != chip8.registers[get_Vy(opcode)]:
        chip8.program_counter += 4
    else:
        chip8.program_counter += 2

def _Annn(chip8: Chip8, opcode):
    """
    LD I, addr

    Set I = nnn.

    The value of register I is set to nnn.
    """
    chip8.I = get_nnn(opcode)
    chip8.program_counter += 2

def _Bnnn(chip8: Chip8, opcode):
    """
    JP V0, addr

    Jump to location nnn + V0.

    The program counter is set to nnn plus the value of V0.
    """
    chip8.program_counter = get_nnn(opcode) + chip8.registers[0]

def _Cxkk(chip8: Chip8, opcode):
    """
    RND Vx, byte

    Set Vx = random byte AND kk.

    The interpreter generates a random number from 0 to 255, 
    which is then ANDed with the value kk. 
    The results are stored in Vx. 
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    chip8.registers[get_Vx(opcode)] = Vx_register_value & random.randint(0, 255)
    chip8.program_counter += 2

def _Dxyn(chip8: Chip8, opcode):
    """
    DRW Vx, Vy, nibble

    Display n-byte sprite starting at memory location I at (Vx, Vy),
    set VF = collision.

    The interpreter reads n bytes from memory, 
    starting at the address stored in I. 
    These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). 
    Sprites are XORed onto the existing screen. 
    If this causes any pixels to be erased, 
    VF is set to 1, 
    otherwise it is set to 0. 
    If the sprite is positioned so part of it is outside the coordinates of the display, 
    it wraps around to the opposite side of the screen.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    Vy_register_value = chip8.registers[get_Vy(opcode)]
    n = get_n(opcode)

    collision = 0
    for i in range(n):
        current_byte_to_display = chip8.memory[chip8.I + i]
        for j in range(8):
            mask = (0x80 >> j)
            current_pixel_to_display = ((current_byte_to_display & mask) >> (7-j)) 
            if (Vy_register_value + i) >= 32 or (j + Vx_register_value) >= 64:
                continue
            display_bit = (Vx_register_value + ((Vy_register_value + i) *64) + j)
            old_pixel = chip8.display[display_bit] 
            chip8.display[display_bit] ^= current_pixel_to_display
            if old_pixel == 1 and chip8.display[display_bit]  == 0:
                collision = 1

    chip8.registers[FLAG_REGISTER] = collision
    chip8.program_counter += 2
    chip8.draw_flag = True

def _E(chip8: Chip8, opcode):
    _E_instructions_map = {
        0x9E: _Ex9E,
        0xA1: _ExA1
    }

    _E_instructions_map[get_kk(opcode)](chip8, opcode)

def _Ex9E(chip8: Chip8, opcode):
    """
    SKP Vx
    
    Skip next opcode if key with the value of Vx is pressed.

    Checks the keyboard, 
    and if the key corresponding to the value of Vx is currently in the down position, 
    PC is increased by 2.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    if chip8.keys[Vx_register_value] == 1:
        chip8.program_counter += 4
    else:
        chip8.program_counter += 2

def _ExA1(chip8: Chip8, opcode):
    """
    SKNP Vx
    
    Skip next opcode if key with the value of Vx is not pressed.

    Checks the keyboard, 
    and if the key corresponding to the value of Vx is currently in the up position, 
    PC is increased by 2.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]

    if chip8.keys[Vx_register_value] == 0:
        chip8.program_counter += 4
    else:
        chip8.program_counter += 2

def _F(chip8: Chip8, opcode):
    _F_instructions_map = {
        0x07: _Fx07,
        0x0A: _Fx0A,
        0x15: _Fx15,
        0x18: _Fx18,
        0x1E: _Fx1E,
        0x29: _Fx29,
        0x33: _Fx33,
        0x55: _Fx55,
        0x65: _Fx65
    }
    _F_instructions_map[get_kk(opcode)](chip8, opcode)


def _Fx07(chip8: Chip8, opcode):
    """
    LD Vx, DT

    Set Vx = delay timer value.

    The value of DT is placed into Vx.
    """
    chip8.registers[get_Vx(opcode)] = chip8.DT
    chip8.program_counter += 2

def _Fx0A(chip8: Chip8, opcode):
    """
    LD Vx, K

    Wait for a key press, 
    store the value of the key in Vx.

    All execution stops until a key is pressed, 
    then the value of that key is stored in Vx.
    """
    for key, keyValue in enumerate(chip8.keys):
        if keyValue == 1:
            chip8.registers[get_Vx(opcode)] = key
            chip8.program_counter += 2
            return

def _Fx15(chip8: Chip8, opcode):
    """
    LD DT, Vx

    Set delay timer = Vx.

    DT is set equal to the value of Vx.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    chip8.DT = Vx_register_value
    chip8.program_counter += 2

def _Fx18(chip8: Chip8, opcode):
    """
    LD ST, Vx
    
    Set sound timer = Vx.

    ST is set equal to the value of Vx.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    chip8.ST = Vx_register_value
    chip8.program_counter += 2

def _Fx1E(chip8: Chip8, opcode):
    """
    ADD I, Vx

    Set I = I + Vx.

    The values of I and Vx are added, 
    and the results are stored in I.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    chip8.I += Vx_register_value
    chip8.program_counter += 2

def _Fx29(chip8: Chip8, opcode):
    """
    LD F, Vx

    Set I = location of sprite for digit Vx.

    The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. 
    
    See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]
    chip8.I = (Vx_register_value * 5)
    chip8.program_counter += 2

def _Fx33(chip8: Chip8, opcode):
    """
    LD B, Vx
    
    Store BCD representation of Vx in memory locations I, I+1, and I+2.

    The interpreter takes the decimal value of Vx, 
    and places the hundreds digit in memory at location in I, 
    the tens digit at location I+1, 
    and the ones digit at location I+2.
    """
    Vx_register_value = chip8.registers[get_Vx(opcode)]

    chip8.memory[chip8.I] = Vx_register_value // 100
    chip8.memory[chip8.I + 1] = (Vx_register_value % 100) // 10
    chip8.memory[chip8.I + 2] = Vx_register_value % 10

    chip8.program_counter += 2

def _Fx55(chip8: Chip8, opcode):
    """
    LD [I], Vx

    Store registers V0 through Vx in memory starting at location I.

    The interpreter copies the values of registers V0 through Vx into memory, 
    starting at the address in I.
    """
    for register_index in range(get_Vx(opcode) + 1):
        chip8.memory[register_index + chip8.I] = chip8.registers[register_index]

    chip8.I += (get_Vx(opcode) + 1)
    chip8.program_counter += 2

def _Fx65(chip8: Chip8, opcode):
    """
    LD Vx, [I]

    Read registers V0 through Vx from memory starting at location I.

    The interpreter reads values from memory starting at location I into registers V0 through Vx.
    """
    for register_index in range(get_Vx(opcode) + 1):
         chip8.registers[register_index] = chip8.memory[register_index + chip8.I]

    chip8.I += (get_Vx(opcode) + 1)
    chip8.program_counter += 2

instruction_map = {
    0x0: _0,
    0x1: _1nnn,
    0x2: _2nnn,
    0x3: _3xkk,
    0x4: _4xkk,
    0x5: _5xy0,
    0x6: _6xkk,
    0x7: _7xkk,
    0x8: _8,
    0x9: _9xy0,
    0xA: _Annn,
    0xB: _Bnnn,
    0xC: _Cxkk,
    0xD: _Dxyn,
    0xE: _E,
    0xF: _F
}

#can be moved to a seperate file probably
def get_nnn(opcode):
    return opcode & 0x0FFF

def get_Vx(opcode):
    return (opcode & 0x0F00) >> 8
    

def get_Vy(opcode):
    return (opcode & 0x00F0) >> 4

def get_kk(opcode):
    return (opcode & 0x00FF)

def get_n(opcode):
    return opcode & 0x000F
