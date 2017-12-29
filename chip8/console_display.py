import logging

import curses

LOG = logging.getLogger(__name__)


class ConsoleDisplay(object):
    def __init__(self, height, width, begin_y, begin_x):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.win = curses.newwin(height, width, begin_y, begin_x)
        self.stdscr.refresh()
        LOG.info('ConsoleDisplay ready')

    def clear(self):
        LOG.info('ConsoleDisplay clear')
        self.win.clear()
        self.stdscr.refresh()

    def draw(self, x, y, char):
        LOG.debug(f'ConsoleDisplay drawing at {x}:{y} - {char}')
        self.stdscr.addch(x, y, char)

    def update(self):
        LOG.debug('ConsoleDisplay refresh')
        self.stdscr.refresh()

    def __del__(self):
        LOG.info('ConsoleDisplay teardown')
        curses.echo()
        curses.nocbreak()
        curses.endwin()

