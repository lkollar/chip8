import logging
import sys
from time import sleep

from chip8.core import Chip8
from chip8.console_display import ConsoleDisplay


def main(args):
    rom = args[1]
    display = ConsoleDisplay(32, 64, 10, 10)
    chip8 = Chip8(display)

    with open(rom, 'rb') as rom_buf:
        chip8.load_rom(rom_buf.read())

    while True:
        chip8.execute_cycle()
        sleep(0.12)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="chip8.log")
    main(sys.argv)
