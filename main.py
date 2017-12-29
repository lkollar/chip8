import io
import logging
import sys

import pygame

from chip8.core import Chip8
from chip8.display import GraphicsDisplay

TIMER = pygame.USEREVENT + 1

LOG = logging.getLogger(__name__)


def main(args):
    rom = args[1]
    display = GraphicsDisplay()
    chip8 = Chip8(display)

    pygame.time.set_timer(TIMER, 17)

    with open(rom, 'rb') as rom_buf:
        chip8.load_rom(rom_buf.read())

    while True:
        pygame.time.wait(17)
        chip8.execute_cycle()

        for event in pygame.event.get():
            if event.type == TIMER:
                pass  # FIXME
            elif event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                LOG.debug("Key pressed: %s", pygame.key.get_pressed())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="chip8.log")
    main(sys.argv)
