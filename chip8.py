from instructions import instruction_map
#setup graphics

#setup input

#initialize other stuff

#load game

#emulation loop
    #do cycle
        #fetch
        #decode
        #execute
        #update timer
    
    #draw if draw flag is set
    
    #grab input

class Chip8(object):
    FLAG_REGISTER  = 0xF
    
    memmory = [0]*4096 #4kb of memmory, 4096 bytes

    #programs start at locations 0x200 - 512
    registers = [0]*16 #general purpose registers, 8 bit. 1byte

    register_I = 0

    stack_pointer = 0
    stack = []

    program_counter = 0 #16 bit executing address

    display = [0] * 64 * 32 # monochrome 64 by 32 pixel display

    def perform_cycle(self):
        opcode = (self.memmory[self.program_counter] << 8) | self.memmory[self.program_counter+1]

        first_byte_of_opcode = opcode & 0xF000 >> 12

        instruction_map[first_byte_of_opcode](self, opcode)
        

    def load_rom(self):
        pass
