import pygame
import random
from sys import argv, exit

DARK = (0, 0, 50)
WHITE = (255, 255, 255)
SIZE = 10

key_map = {
    49: 1, 50: 2, 51: 3, 52: 0xc,
    113: 4, 119: 5, 101: 6, 114: 0xd,
    97: 7, 115: 8, 100: 9, 102: 0xe,
    122: 0xa, 120: 0, 99: 0xb, 118: 0xf
}

class Chip8:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))
        
        self.clock = pygame.time.Clock()
        self.memory = bytearray(4096)
        self.V = bytearray(16)  # Registers V0 to VF
        self.I = 0  # Index register
        self.pc = 0x200  # Program counter starts at 0x200
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.enable_sound = False
        self.display = bytearray(64 * 32)  # 64x32 display, 1D array
        self.keys = [False] * 16
        self.load_fonts()
        self.window = pygame.display.set_mode((64 * SIZE, 32 * SIZE))

    def load_fonts(self):
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        for i, byte in enumerate(fontset):
            self.memory[i] = byte

    def emulate_cycle(self):
        # Fetch the next opcode
        opcode_bytes = self.memory[self.pc:self.pc + 2]
        # Convert the byte string to an integer
        opcode = int.from_bytes(opcode_bytes, byteorder='big')
        self.pc += 2
        self.execute_opcode(opcode)

    def execute_opcode(self, opcode):
        instruction = opcode & 0xF000
        x = (opcode & 0x0F00) >> 8  # second nibble
        y = (opcode & 0x00F0) >> 4  # third nibble
        n = opcode & 0x000F  # last nibble
        nn = opcode & 0x00FF  # second byte
        nnn = opcode & 0x0FFF  # last 3 nibbles

        if opcode == 0x00E0:
            # Clear the display
            self.display = bytearray(64 * 32)
        elif opcode == 0x00EE:
            # Return from a subroutine
            self.pc = self.stack.pop()
        elif instruction == 0x1000:
            # Jump to address nnn
            self.pc = nnn
        elif instruction == 0x2000:
            # Call subroutine at nnn
            self.stack.append(self.pc)
            self.pc = nnn
        elif instruction == 0x3000:
            # Skip next instruction if Vx == nn
            if self.V[x] == nn:
                self.pc += 2
        elif instruction == 0x4000:
            # Skip next instruction if Vx != nn
            if self.V[x] != nn:
                self.pc += 2
        elif instruction == 0x5000:
            # Skip next instruction if Vx == Vy
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif instruction == 0x6000:
            # Set Vx to nn
            self.V[x] = nn
        elif instruction == 0x7000:
            # Add nn to Vx
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif (opcode & 0xF00F) == 0x8000:
            # Set Vx to the value of Vy
            self.V[x] = self.V[y]
        elif (opcode & 0xF00F) == 0x8001:
            # Set Vx to Vx OR Vy
            self.V[x] |= self.V[y]
        elif (opcode & 0xF00F) == 0x8002:
            # Set Vx to Vx AND Vy
            self.V[x] &= self.V[y]
        elif (opcode & 0xF00F) == 0x8003:
            # Set Vx to Vx XOR Vy
            self.V[x] ^= self.V[y]
        elif (opcode & 0xF00F) == 0x8004:
            # Add Vy to Vx, set VF to carry
            result = self.V[x] + self.V[y]
            self.V[0xF] = 1 if result > 0xFF else 0
            self.V[x] = result & 0xFF
        elif (opcode & 0xF00F) == 0x8005:
            # Subtract Vy from Vx, set VF to NOT borrow
            self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF
        elif (opcode & 0xF00F) == 0x8006:
            # Shift Vx right by one, set VF to least significant bit prior to shift
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] >>= 1
        elif (opcode & 0xF00F) == 0x8007:
            # Set Vx to Vy minus Vx, set VF to NOT borrow
            self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF
        elif (opcode & 0xF00F) == 0x800E:
            # Shift Vx left by one, set VF to most significant bit prior to shift
            self.V[0xF] = (self.V[x] & 0x80) >> 7
            self.V[x] = (self.V[x] << 1) & 0xFF
        elif (opcode & 0xF00F) == 0x9000:
            # Skip next instruction if Vx != Vy
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif instruction == 0xA000:
            # Set I to nnn
            self.I = nnn
        elif instruction == 0xB000:
            # Jump to address nnn + V0
            self.pc = nnn + self.V[0]
        elif instruction == 0xC000:
            # Set Vx to a random number AND nn
            self.V[x] = random.randint(0, 255) & nn
        elif instruction == 0xD000:
            # Draw a sprite at position Vx, Vy with n bytes of sprite data starting at I
            self.draw_sprite(self.V[x], self.V[y], n)
        elif (opcode & 0xF0FF) == 0xE09E:
            # Skip next instruction if key with the value of Vx is pressed
            if self.keys[self.V[x]]:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xE0A1:
            # Skip next instruction if key with the value of Vx is not pressed
            if not self.keys[self.V[x]]:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xF007:
            # Set Vx to the value of the delay timer
            self.V[x] = self.delay_timer
        elif (opcode & 0xF0FF) == 0xF00A:
            # Wait for a key press, store the value of the key in Vx
            key = None
            while key is None:
                self.keyhandler()
                for i in range(16):
                    if self.keys[i]:
                        key = i
                        break
            self.V[x] = key
        elif (opcode & 0xF0FF) == 0xF015:
            # Set the delay timer to Vx
            self.delay_timer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF018:
            # Set the sound timer to Vx
            self.sound_timer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF01E:
            # Add Vx to I
            self.I = (self.I + self.V[x]) & 0xFFFF
        elif (opcode & 0xF0FF) == 0xF029:
            # Set I to the location of the sprite for the character in Vx
            self.I = self.V[x] * 5
        elif (opcode & 0xF0FF) == 0xF033:
            # Store the binary-coded decimal representation of Vx at I, I+1, and I+2
            self.memory[self.I] = self.V[x] // 100
            self.memory[self.I + 1] = (self.V[x] // 10) % 10
            self.memory[self.I + 2] = self.V[x] % 10
        elif (opcode & 0xF0FF) == 0xF055:
            # Store registers V0 to Vx in memory starting at I
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]
        elif (opcode & 0xF0FF) == 0xF065:
            # Read registers V0 to Vx from memory starting at I
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]
        else:
            print(f"Unknown opcode: {opcode:04X}")

    def load_rom(self, rom_path):
        # Load the ROM into memory starting at 0x200
        with open(rom_path, 'rb') as rom:
            rom_data = rom.read()
            for i, byte in enumerate(rom_data):
                self.memory[0x200 + i] = byte

    def draw_sprite(self, x, y, height):
        self.V[0xF] = 0  # Reset the collision flag (VF register)
        for row in range(height):
            sprite_byte = self.memory[self.I + row]  # Get the byte of the sprite from memory
            for col in range(8):
                # Check if the current bit is set (each byte represents 8 pixels)
                if sprite_byte & (0x80 >> col):
                    # Calculate the index in the display array
                    index = ((x + col) % 64) + ((y + row) % 32) * 64
                    # Check for collision: if the pixel is already set
                    if self.display[index]:
                        self.V[0xF] = 1  # Set the collision flag if there is a collision
                    # Draw the pixel using XOR (toggle the pixel)
                    self.display[index] ^= 1

    def keyhandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in key_map:
                    self.keys[key_map[event.key]] = True
            elif event.type == pygame.KEYUP:
                if event.key in key_map:
                    self.keys[key_map[event.key]] = False

    def update_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            pygame.mixer.Sound('beep.wav').play()
            self.sound_timer -= 1

    def mainloop(self):
        while True:
            self.clock.tick(60)
            self.keyhandler()
            self.emulate_cycle()
            self.update_timers()
            self.window.fill(DARK)
            for y in range(32):
                for x in range(64):
                    if self.display[x + y * 64]:
                        pygame.draw.rect(self.window, WHITE, (x * SIZE, y * SIZE, SIZE, SIZE))
            pygame.display.flip()

if __name__ == "__main__":
    message = """

 ██████╗██╗  ██╗██╗██████╗        █████╗     ███████╗███╗   ███╗██╗   ██╗██╗      █████╗ ████████╗ ██████╗ ██████╗ 
██╔════╝██║  ██║██║██╔══██╗      ██╔══██╗    ██╔════╝████╗ ████║██║   ██║██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
██║     ███████║██║██████╔╝█████╗╚█████╔╝    █████╗  ██╔████╔██║██║   ██║██║     ███████║   ██║   ██║   ██║██████╔╝
██║     ██╔══██║██║██╔═══╝ ╚════╝██╔══██╗    ██╔══╝  ██║╚██╔╝██║██║   ██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗
╚██████╗██║  ██║██║██║           ╚█████╔╝    ███████╗██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║
 ╚═════╝╚═╝  ╚═╝╚═╝╚═╝            ╚════╝     ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                                                                                   

            """
    print(message)
    if len(argv) != 2:
        print("Usage: python chip.py <path_to_rom>")
        exit()

    chip8 = Chip8()
    chip8.load_rom(argv[1])
    chip8.mainloop()
