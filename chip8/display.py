# -*- coding: future_fstrings -*-

import logging

import pygame

SCALE_FACTOR = 10
COLOUR_BLACK = pygame.Color(0, 0, 0, 255)
COLOUR_WHITE = pygame.Color(255, 255, 255, 255)

COLOURS = {
    0: COLOUR_BLACK,
    1: COLOUR_WHITE
}

LOG = logging.getLogger(__name__)


class GraphicsDisplay:
    def __init__(self):
        LOG.info("Creating display")
        pygame.init()
        pygame.display.init()
        self.surface = pygame.display.set_mode(
            (64 * SCALE_FACTOR, 32 * SCALE_FACTOR),
            pygame.HWSURFACE | pygame.DOUBLEBUF, 8)
        pygame.display.set_caption('CHIP8')
        self.clear()

    def draw(self, x_start, y_start, n, source):
        collision = False
        for y in range(n):
            sprite = source[y]
            for x in range(8):
                pixel = (sprite >> (7 - x)) & 1
                new_x = x_start + x
                new_x = new_x % 64
                new_y = y_start + y
                new_y = new_y % 32
                new_pixel = pixel ^ self._is_pixel_set(new_x, new_y)
                if new_pixel != pixel:
                    collision = True
                self._draw(new_x, new_y, COLOURS[new_pixel])
        pygame.display.flip()
        return collision

    def _draw(self, x, y, colour):
        LOG.debug(f"Drawing pixel at x:{x * SCALE_FACTOR} y:{y * SCALE_FACTOR} colour:{colour}")
        self.surface.fill(colour,
                          (x * SCALE_FACTOR,
                           y * SCALE_FACTOR,
                           SCALE_FACTOR,
                           SCALE_FACTOR))

    def _is_pixel_set(self, x, y):
        colour = self.surface.get_at((x * SCALE_FACTOR, y * SCALE_FACTOR))
        return colour == COLOUR_WHITE

    def clear(self):
        self.surface.fill(COLOUR_BLACK)
        pygame.display.flip()
