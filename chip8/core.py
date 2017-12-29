# -*- coding: future_fstrings -*-

import logging
import random

import binascii

from chip8.sprites import SPRITES


LOG = logging.getLogger(__name__)

PC_START_ADDRESS = 0x200


class Chip8(object):
    def __init__(self, display, debug_stream=None):
        self.display = display
        self.memory = bytearray(4096)
        self.v = bytearray(16)
        self.register_i = bytearray(2)
        self.dt = bytearray(1)
        self.dt = 0
        self.st = bytearray(1)
        self.pc = PC_START_ADDRESS
        self.stack_ptr = 0
        self.stack = [0] * 16
        self.key = False
        self._init_sprites()
        self.debug_stream = debug_stream
        self.cycles = 0
        random.seed()

    def _init_sprites(self):
        """Initialise memory with sprites.

        0x000 to 0x1FF in the main memory contains 16 sprites."""
        address = 0
        for sprite in SPRITES:
            for sprite_byte in sprite:
                self.memory[address] = sprite_byte
                address += 1

    def load_rom(self, rom_buffer):
        for index, val in enumerate(rom_buffer):
            self.memory[0x200 + index] = val
        self.pc = 0x200

    def execute_cycle(self):
        # LOG.debug("PC:{}".format(hex(self.pc)))

        i1 = self.memory[self.pc]
        i2 = self.memory[self.pc + 1]

        if self.debug_stream:
            self.dump_status(hex(i1 << 8 | i2))

        self.pc += 2
        if self.dt > 0:
            self.dt -= 1
        self.decode_instruction(i1 << 8 | i2)
        self.cycles += 1

    def key_pressed(self, key):
        self.key = key

    def dump_status(self, opcode):
        try:
            reg_i = hex(self.register_i)
        except TypeError:
            reg_i = 0

        stats = f'[{self.cycles}] Opcode: {opcode}\tI: {reg_i}\tPC: {hex(self.pc)}\n'
        stats += f'Stack: {self.stack}\tSP: {self.stack_ptr}\n'
        for i in range(16):
            stats += f"V{i}: {hex(self.v[i])} "
        stats += "\n\n"
        self.debug_stream.write(unicode(stats))

    # INSTRUCTIONS

    def call_rca(self, _):
        LOG.debug("call_rca")
        assert False, "call_rca - Not implemented"

    def cls(self):
        LOG.debug("disp_clear")
        self.display.clear()

    def ret(self):
        LOG.debug("ret")
        self.pc = self.stack[self.stack_ptr]
        self.stack_ptr -= 1

    def jump(self, nnn):
        LOG.debug("goto")
        self.pc = nnn

    def call(self, nnn):
        LOG.debug("call nnn={}".format(hex(nnn)))
        self.stack_ptr += 1
        self.stack[self.stack_ptr] = self.pc
        self.pc = nnn

    def skipinst_vx_eq_nn(self, x, nn):
        LOG.debug("skipinst_vx_eq_nn")
        if self.v[x] == nn:
            self.pc += 2

    def skipinst_vx_neq_nn(self, x, nn):
        LOG.debug("skipinst_vx_neq_nn")
        if self.v[x] != nn:
            self.pc += 2

    def skipinst_vx_eq_vy(self, x, y):
        if self.v[x] == self.v[y]:
            self.pc += 2

    # 6XNN
    def set_vx_to_nn(self, x, nn):
        LOG.debug("set_vx_to_nn")
        self.v[x] = nn

    # 7XNN
    def add_nn_to_vx(self, x, nn):
        LOG.debug("add_nn_to_vx")
        self.v[x] = (self.v[x] + nn) & 0xff

    # 8XY0
    def set_vx_to_vy(self, x, y):
        LOG.debug("set_vx_to_vy")
        self.v[x] = self.v[y]

    # 8XY1
    def set_vx_to_vx_or_vy(self, x, y):
        LOG.debug("set_vx_to_vx_or_vy")
        self.v[x] = self.v[x] | self.v[y]

    # 8XY2
    def set_vx_to_vx_and_vy(self, x, y):
        LOG.debug("set_vx_to_vx_and_vy")
        self.v[x] = self.v[x] & self.v[y]

    # 8XY3
    def set_vx_to_vx_xor_vy(self, x, y):
        LOG.debug("set_vx_to_vx_xor_vy")
        self.v[x] = self.v[x] ^ self.v[y]

    # 8XY4
    def add_vy_to_vx(self, x, y):
        LOG.debug("add_vy_to_vx")
        # TODO review this
        result = self.v[x] + self.v[y]
        if result > 0xff:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[x] = result & 0xff

    # 8XY5
    def sub_vy_from_vx(self, x, y):
        """Vx = Vx - Vy, set VF = NOT borrow."""
        LOG.debug("sub_vy_from_vx")
        if self.v[x] < self.v[y]:
            self.v[0xf] = 0
            self.v[x] = self.v[x] + 0x100 - self.v[y]
        else:
            self.v[0xf] = 1
            self.v[x] = self.v[x] - self.v[y]

    # 8XY6
    def shift_r_vy_to_vx(self, x, y):
        """Set Vx = Vx SHR 1."""
        LOG.debug("shift_r_vy_to_vx")
        self.v[0xf] = self.v[y] & 0x1
        self.v[x] = self.v[y] >> 1

    # 8XY7
    def set_vx_to_vy_min_vx(self, x, y):
        """Set Vx = Vy - Vx, set VF = NOT borrow."""
        LOG.debug("set_vx_to_vy_min_vx")
        if self.v[y] < self.v[x]:
            self.v[0xf] = 0
            self.v[x] = 0x100 + self.v[y] - self.v[x]
        else:
            self.v[0xf] = 1
            self.v[x] = self.v[y] - self.v[x]

    # 8XYE
    def shift_l_vy_to_vx(self, x, y):
        """Set Vx = Vx SHL 1."""
        LOG.debug("shift_l_vy_to_vx")
        self.v[0xf] = self.v[y] >> 7
        result = self.v[y] << 1
        self.v[x] = result & 0xff


    # 9XY0
    def skip_inst_if_vx_neq_vy(self, x, y):
        LOG.debug("skip_inst_if_vx_neq_vy")
        if self.v[x] != self.v[y]:
            self.pc += 2

    # ANNN
    def set_i_to_nnn(self, nnn):
        LOG.debug("set_i_to_nnn")
        self.register_i = nnn

    # BNNN
    def jump_to_v0_plus_nnn(self, nnn):
        LOG.debug("jump_to_v0_plus_nnn")
        self.pc = nnn + self.v[0]

    # CXNN
    def set_vx_rand_and_nn(self, x, nn):
        LOG.debug("set_vx_rand_and_nn")
        rnd = random.randrange(0, 255)
        self.v[x] = rnd & nn

    # DXYN
    def draw_sprite(self, x, y, n):
        LOG.debug("draw_sprite")
        sprite_data = self.memory[self.register_i:self.register_i+n]
        collision = self.display.draw(self.v[x], self.v[y], n, sprite_data)
        self.v[0xf] = 1 if collision else 0

    # EX9E
    def skip_inst_if_vx_pressed(self, x):
        LOG.debug("skip_inst_if_vx_pressed")
        if self.key and self.key == self.v[x]:
            self.pc += 2

    # EXA1
    def skip_inst_if_vx_not_pressed(self, x):
        LOG.debug("skip_inst_if_vx_not_pressed")
        if not self.key or (self.key and self.key != self.v[x]):
            self.pc += 2

    # FX07
    def set_vx_to_delay_timer(self, x):
        LOG.debug("set_vx_to_delay_timer")
        self.v[x] = self.dt

    # FX0A
    def wait_key_store_vx(self, x):
        LOG.debug("wait_key_store_vx")
        # FIXME

    # FX15
    def set_delay_timer_to_vx(self, x):
        LOG.debug("set_delay_timer_to_vx")
        self.dt = self.v[x]

    # FX18
    def set_sound_timer_to_vx(self, x):
        LOG.debug("set_sound_timer_to_vx")
        self.st = self.v[x]

    # FX1E
    def add_vx_to_i(self, x):
        LOG.debug("add_vx_to_i")
        self.register_i = self.register_i + self.v[x]

    # FX29
    def set_i_to_sprite_in_vx(self, x):
        LOG.debug("set_i_to_sprite_in_vx")
        self.register_i = self.v[x] * 5

    # FX33
    def set_i_to_bcd(self, x):
        LOG.debug("set_i_to_bcd")
        value = str(self.v[x])
        self.memory[self.register_i] = int(value[2])
        self.memory[self.register_i + 1] = int(value[1])
        self.memory[self.register_i + 2] = int(value[0])

    # FX55
    def reg_dump_to_mem(self, x):
        LOG.debug("reg_dump_to_mem")
        for i in range(x+1):
            self.memory[self.register_i + i] = self.v[i]

        self.register_i += x + 1

    # FX65
    def reg_load_from_mem(self, x):
        LOG.debug("reg_load_from_mem")
        for i in range(x+1):
            self.v[i] = self.memory[self.register_i + i]
        self.register_i += x + 1

    def decode_instruction(self, instruction):
        """
        :type instruction:int
        """
        _1 = (instruction >> 12) & 0xf
        _2 = (instruction >> 8) & 0xf
        _3 = (instruction >> 4) & 0xf
        _4 = instruction & 0xf
        # LOG.debug("opcode: {}".format(hex(instruction)))

        if _1 == 0:
            if _3 == 0xe & _4 == 0xe:
                self.ret()
            elif _3 == 0xe:
                self.cls()
            else:
                self.call_rca(instruction & 0x0fff)
        elif _1 == 1:
            self.jump(instruction & 0x0fff)
        elif _1 == 2:
            self.call(instruction & 0x0fff)
        elif _1 == 3:
            self.skipinst_vx_eq_nn(_2, instruction & 0x00ff)
        elif _1 == 4:
            self.skipinst_vx_neq_nn(_2, instruction & 0x00ff)
        elif _1 == 5:
            self.skipinst_vx_eq_vy(_2, _3)
        elif _1 == 6:
            self.set_vx_to_nn(_2, instruction & 0x00ff)
        elif _1 == 7:
            self.add_nn_to_vx(_2, instruction & 0x00ff)
        elif _1 == 8:
            if _4 == 0:
                self.set_vx_to_vy(_2, _3)
            elif _4 == 1:
                self.set_vx_to_vx_or_vy(_2, _3)
            elif _4 == 2:
                self.set_vx_to_vx_and_vy(_2, _3)
            elif _4 == 3:
                self.set_vx_to_vx_xor_vy(_2, _3)
            elif _4 == 4:
                self.add_vy_to_vx(_2, _3)
            elif _4 == 5:
                self.sub_vy_from_vx(_2, _3)
            elif _4 == 6:
                self.shift_r_vy_to_vx(_2, _3)
            elif _4 == 7:
                self.set_vx_to_vy_min_vx(_2, _3)
            elif _4 == 0xe:
                self.shift_l_vy_to_vx(_2, _3)
            else:
                raise RuntimeError('Failed to decode instruction')
        elif _1 == 9:
            self.skip_inst_if_vx_neq_vy(_2, _3)
        elif _1 == 0xa:
            self.set_i_to_nnn(instruction & 0x0fff)
        elif _1 == 0xb:
            self.jump_to_v0_plus_nnn(instruction & 0xfff)
        elif _1 == 0xc:
            self.set_vx_rand_and_nn(_2, instruction & 0x00ff)
        elif _1 == 0xd:
            self.draw_sprite(_2, _3, _4)
        elif _1 == 0xe and _3 == 0x9:
            self.skip_inst_if_vx_pressed(_2)
        elif _1 == 0xe and _3 == 0xa:
            self.skip_inst_if_vx_not_pressed(_2)
        elif _1 == 0xf:
            if _4 == 7:
                self.set_vx_to_delay_timer(_2)
            elif _4 == 0xa:
                self.wait_key_store_vx(_2)
            elif _4 == 5 and _3 == 1:
                self.set_delay_timer_to_vx(_2)
            elif _4 == 8:
                self.set_sound_timer_to_vx(_2)
            elif _4 == 0xe:
                self.add_vx_to_i(_2)
            elif _4 == 9:
                self.set_i_to_sprite_in_vx(_2)
            elif _4 == 3:
                self.set_i_to_bcd(_2)
            elif _4 == 5 and _3 == 5:
                self.reg_dump_to_mem(_2)
            elif _4 == 5 and _3 == 6:
                self.reg_load_from_mem(_2)
            else:
                raise RuntimeError('Failed to decode instruction')
        else:
            raise RuntimeError('Failed to decode instruction')
