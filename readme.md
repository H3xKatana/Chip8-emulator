## Recoursues
    -chip 8 refrence code http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
    -tests https://github.com/corax89/chip8-test-rom
    -https://github.com/mattmikolay/chip-8/wiki/CHIP%E2%80%908-Technical-Reference



## Features

- Emulates the CHIP-8 instruction set
- Renders graphics using Pygame
- Supports original CHIP-8 ROMs and programs like Pong, Tetris, Cave Game, and more

## How to Run

1. **Install Dependencies:**
   Ensure you have Python and Pygame installed. You can install Pygame using pip:
   ```sh
   pip install pygame
   ```

2. **Clone the Repository:**
   ```sh
   git clone https://github.com/H3xKatana/Chip8-emulator.git
   cd Chip8-emulator
   ```

3. **Run the Emulator:**
   ```sh
   python chip.py <path_to_rom>
   ```
   Replace `<path_to_rom>` with the path to your CHIP-8 ROM file.

## Key Mapping

| Key  | CHIP-8 Key |
|------|------------|
| 1    | 1          |
| 2    | 2          |
| 3    | 3          |
| 4    | C          |
| Q    | 4          |
| W    | 5          |
| E    | 6          |
| R    | D          |
| A    | 7          |
| S    | 8          |
| D    | 9          |
| F    | E          |
| Z    | A          |
| X    | 0          |
| C    | B          |
| V    | F          |

## Project Structure

- `chip.py`: Main emulator code.
- `beep.wav`: Sound file for the CHIP-8 sound timer.
- `README.md`: Project documentation.

## How It Works

The emulator is built around the main `Chip8` class, which handles:

- **Memory Management:** Emulates the 4KB memory space of the CHIP-8.
- **Registers:** 16 general-purpose 8-bit registers (V0 to VF) and special-purpose registers like the index register (I) and the program counter (pc).
- **Timers:** Implements delay and sound timers.
- **Graphics:** 64x32 monochrome display managed by a 1D array.
- **Input Handling:** Maps keyboard inputs to CHIP-8 keys.

### Emulator Cycle

The emulator follows a simple loop:
1. Fetch the next opcode from memory.
2. Decode and execute the opcode.
3. Update timers and handle input.
4. Render the display.

## Example

To run a ROM, use the following command:
```sh
python chip.py path/to/your/rom.ch8
```

Replace `path/to/your/rom.ch8` with the actual path to your CHIP-8 ROM file.

## License

This project is open source and available under the [MIT License](LICENSE).

---



## Technical Details

### Memory Layout
- **0x000-0x1FF**: Reserved for the interpreter.
- **0x200-0xFFF**: Program ROM and work RAM.
    Memory Map:
+---------------+= 0xFFF (4095) End of Chip-8 RAM
|               |
|               |
|               |
|               |
|               |
| 0x200 to 0xFFF|
|     Chip-8    |
| Program / Data|
|     Space     |
|               |
|               |
|               |
+- - - - - - - -+= 0x600 (1536) Start of ETI 660 Chip-8 programs
|               |
|               |
|               |
+---------------+= 0x200 (512) Start of most Chip-8 programs
| 0x000 to 0x1FF|
| Reserved for  |
|  interpreter  |
+---------------+= 0x000 (0) Start of Chip-8 RAM



### Registers

- **V0-VF**: 16 general-purpose 8-bit registers. VF is also used as a flag for some operations.
- **I**: 16-bit register for memory addresses (only the lowest 12 bits are used).
- **PC**: Program counter, 16-bit, starts at 0x200.
- **SP**: Stack pointer for 16-level stack.
- **DT**: Delay timer.
- **ST**: Sound timer.

### Display

- 64x32 monochrome display.
- Each pixel is either on (1) or off (0).

### Opcodes

The CHIP-8 has 35 opcodes, each of which is 2 bytes long. Here are some examples of the implemented opcodes:

- **0x00E0**: Clears the screen.
- **0x1NNN**: Jumps to address NNN.
- **0x6XNN**: Sets VX to NN.
- **0x7XNN**: Adds NN to VX.
- **0xANNN**: Sets I to the address NNN.
- **0xDXYN**: Draws a sprite at coordinate (VX, VY) with a width of 8 pixels and a height of N pixels.
- **0xFX1E**: Adds VX to I.

### Timers

The delay and sound timers decrement at a rate of 60Hz. The sound timer plays a sound when it reaches zero.

### Sprite Drawing

- Sprites are drawn at the coordinates specified by the VX and VY registers.
- Each sprite is 8 pixels wide and can be up to 15 pixels tall.
- Sprites are XORed onto the display; if this causes any pixels to be erased, VF is set to 1.

### Input Handling

- The emulator checks for key presses mapped to the CHIP-8 keypad.
- Uses a dictionary to map Pygame key events to CHIP-8 keys.

## Project Structure

- `chip.py`: Main emulator code.
- `beep.wav`: Sound file for the CHIP-8 sound timer.
- `README.md`: Project documentation.

## Example

To run a ROM, use the following command:
```sh
python chip.py path/to/your/rom.ch8
```

Replace `path/to/your/rom.ch8` with the actual path to your CHIP-8 ROM file.

## License

This project is open source and available under the [MIT License](LICENSE).

