from mock import Mock, patch

import pytest

from chip8.core import Chip8, PC_START_ADDRESS


class TestChip8:

    def setup_method(self):
        self.display = Mock()
        self.machine = Chip8(self.display)

    def teardown_method(self):
        self.display = None
        self.machine = None

    def test_CLS(self):
        self.machine.decode_instruction(0x00e0)
        self.display.clear.assert_called_once_with()

    def test_RET(self):
        self.machine.decode_instruction(0x2fff)  # call 0xfff
        self.machine.decode_instruction(0x00ee)  # ret
        assert self.machine.pc == 0x200

    def test_JP(self):
        self.machine.decode_instruction(0x1fff)  # goto 0xfff
        assert self.machine.pc == 0xfff

    def test_SE(self):
        self.machine.v[0] = 0xff
        self.machine.decode_instruction(0x30ff)  # skip next instruction if V0 == 0xff
        assert self.machine.pc == PC_START_ADDRESS + 2

    def test_SE_negative(self):
        self.machine.v[0] = 0xfe
        self.machine.decode_instruction(0x30ff)  # skip next instruction if V0 == 0xff
        assert self.machine.pc == PC_START_ADDRESS

    def test_SNE(self):
        self.machine.v[0] = 0xfe
        self.machine.decode_instruction(0x40ff)  # skip next instruction if V0 != 0xff
        assert self.machine.pc == PC_START_ADDRESS + 2

    def test_SNE_negative(self):
        self.machine.v[0] = 0xff
        self.machine.decode_instruction(0x40ff)  # skip next instruction if V0 != 0xff
        assert self.machine.pc == PC_START_ADDRESS

    def test_SE_regs(self):
        self.machine.v[0] = 0xfe
        self.machine.v[1] = 0xfe
        self.machine.decode_instruction(0x5010)  # skip next instruction if V0 == V1
        assert self.machine.pc == PC_START_ADDRESS + 2

    def test_SE_regs_negative(self):
        self.machine.v[0] = 0xff
        self.machine.v[1] = 0xfe
        self.machine.decode_instruction(0x5010)  # skip next instruction if V0 == V1
        assert self.machine.pc == PC_START_ADDRESS

    def test_LD_byte(self):
        self.machine.decode_instruction(0x60ff)
        assert self.machine.v[0] == 0xff

    def test_ADD_byte(self):
        self.machine.decode_instruction(0x600f)
        self.machine.decode_instruction(0x70ff)
        assert self.machine.v[0] == 0xe

    def test_ADD_overflow(self):
        self.machine.v[0] = 1
        self.machine.decode_instruction(0x7001)
        assert self.machine.v[0] == 2

    def test_LD_reg(self):
        self.machine.v[0] = 0
        self.machine.v[1] = 0xf
        self.machine.decode_instruction(0x8010)  # store the value of V1 in V0
        assert self.machine.v[0] == 0xf

    def test_OR(self):
        self.machine.v[0] = 3
        self.machine.v[1] = 4
        self.machine.decode_instruction(0x8011)  # store the value of V0 | V1 in V0
        assert self.machine.v[0] == 7

    def test_AND(self):
        self.machine.v[0] = 0xa
        self.machine.v[1] = 7
        self.machine.decode_instruction(0x8012)  # store the value of V0 & V1 in V0
        assert self.machine.v[0] == 2

    def test_XOR(self):
        self.machine.v[0] = 0xa
        self.machine.v[1] = 7
        self.machine.decode_instruction(0x8013)  # store the value of V0 ^ V1 in V0
        assert self.machine.v[0] == 0xd

    def test_ADD_no_carry(self):
        self.machine.decode_instruction(0x6001)
        self.machine.decode_instruction(0x6102)
        self.machine.decode_instruction(0x8014)  # store the value of V0 + V1 in V0
        assert self.machine.v[0] == 3
        assert self.machine.v[0xf] == 0

    def test_ADD_carry(self):
        self.machine.decode_instruction(0x60ff)
        self.machine.decode_instruction(0x61ff)
        self.machine.decode_instruction(0x8014)  # store the value of V0 + V1 in V0
        assert self.machine.v[0] == 0xfe
        assert self.machine.v[0xf] == 1

    def test_SUB(self):
        self.machine.decode_instruction(0x60ff)
        self.machine.decode_instruction(0x6103)
        self.machine.decode_instruction(0x8015)  # store the value of V0 - V1 in V0
        assert self.machine.v[0] == 0xfc
        assert self.machine.v[0xf] == 1

    def test_SUB_borrow(self):
        self.machine.decode_instruction(0x6000)
        self.machine.decode_instruction(0x6101)
        self.machine.decode_instruction(0x8015)  # store the value of V0 - V1 in V0
        assert self.machine.v[0] == 0xff
        assert self.machine.v[0xf] == 0

    def test_SHR_no_carry(self):
        self.machine.decode_instruction(0x6000)
        self.machine.decode_instruction(0x6104)
        self.machine.decode_instruction(0x8016)  # store the value of V0 >> 1 in V0
        assert self.machine.v[0] == 0x02
        assert self.machine.v[0xf] == 0

    def test_SHR_carry(self):
        self.machine.decode_instruction(0x6000)
        self.machine.decode_instruction(0x6103)
        self.machine.decode_instruction(0x8016)  # store the value of V0 >> 1 in V0
        assert self.machine.v[0] == 1
        assert self.machine.v[0xf] == 1

    def test_SUBN_borrow(self):
        self.machine.decode_instruction(0x6001)
        self.machine.decode_instruction(0x610f)
        self.machine.decode_instruction(0x8017)  # store the value of V1 - V0 in V0
        assert self.machine.v[0] == 0xe
        assert self.machine.v[0xf] == 1

    def test_SUBN_no_borrow(self):
        self.machine.decode_instruction(0x600f)
        self.machine.decode_instruction(0x6101)
        self.machine.decode_instruction(0x8017)  # store the value of V1 - V0 in V0
        assert self.machine.v[0] == 0xf2
        assert self.machine.v[0xf] == 0

    def test_SUBN_no_borrow_2(self):
        self.machine.v[0] = 0xf
        self.machine.v[1] = 0xf
        self.machine.decode_instruction(0x8017)  # store the value of V1 - V0 in V0
        assert self.machine.v[0] == 0
        assert self.machine.v[0xf] == 0

    def test_SHL_no_borrow(self):
        self.machine.decode_instruction(0x6000)
        self.machine.decode_instruction(0x6101)
        self.machine.decode_instruction(0x801e)  # store the value of V0 << 1 in V0
        self.machine.v[0] = 0x10
        assert self.machine.v[0xf] == 0

    def test_SHL_borrow(self):
        self.machine.decode_instruction(0x6000)
        self.machine.decode_instruction(0x61c0)
        self.machine.decode_instruction(0x801e)  # store the value of V0 << 1 in V0
        self.machine.v[0] = 0x80
        assert self.machine.v[0xf] == 1

    def test_SNE_reg(self):
        self.machine.v[0] = 0xf
        self.machine.v[1] = 0
        self.machine.decode_instruction(0x9010)  # skip next instruction if V0 != vy
        assert self.machine.pc == PC_START_ADDRESS + 2

    def test_SNE__reg_negative(self):
        self.machine.v[0] = 0xf
        self.machine.v[1] = 0xf
        self.machine.decode_instruction(0x9010)  # skip next instruction if V0 != vy
        assert self.machine.pc == PC_START_ADDRESS

    def test_LD(self):
        self.machine.decode_instruction(0xafff)  # set I to 0xFFF
        assert self.machine.register_i == 0xfff
        
    def test_JP_V0(self):
        self.machine.v[0] = 2
        self.machine.decode_instruction(0xb210)  # set PC to 0x210 + V0
        assert self.machine.pc == 0x212

    @patch('chip8.core.random.randrange')
    def test_RND(self, rand_mock):
        rand_mock.return_value = 9
        self.machine.decode_instruction(0xc005)  # set V0 to random number & 0x10
        assert self.machine.v[0] == 1

    @pytest.mark.skip
    def test_DRW(self):
        # Display sprite starting at memory location in I to V0, V1 coordinates. Set
        # VF to 1 if there is a collission
        self.machine.decode_instruction(0xd015)

    @pytest.mark.skip
    def test_SKP(self):
        self.machine.decode_instruction(0xe09e)

    @pytest.mark.skip
    def test_SKMP(self):
        self.machine.decode_instruction(0xe0a1)

    def test_LD_VX_DT(self):
        self.machine.dt = 5
        self.machine.decode_instruction(0xf007)  # DT is placed into V0
        assert self.machine.v[0] == 5

    @pytest.mark.skip
    def test_LD_VX_K(self):
        self.machine.decode_instruction(0xf00a)  # wait for key and place into V0

    def test_LD_DT_VX(self):
        self.machine.v[0] = 5
        self.machine.decode_instruction(0xf015)  # V0 is placed into DT
        assert self.machine.dt == 5

    def test_LD_ST_VX(self):
        self.machine.v[0] = 5
        self.machine.decode_instruction(0xf018)  # V0 is placed into ST
        assert self.machine.st == 5

    def test_ADD_I_VX(self):
        self.machine.register_i = 4
        self.machine.v[0] = 5
        self.machine.decode_instruction(0xf01e)  # I is set to I + V0
        assert self.machine.register_i == 9

    def test_LD_F_VX(self):
        self.machine.v[0] = 1
        self.machine.decode_instruction(0xf029)  # I is set to location of sprite in V0
        assert self.machine.register_i == 0x06

    def test_LD_B_VX(self):
        self.machine.register_i = 0x300
        self.machine.v[0] = 123
        self.machine.decode_instruction(0xf033)  # I, I+1, I+3 are set to BCD of V0
        assert self.machine.memory[0x302] == 1
        assert self.machine.memory[0x301] == 2
        assert self.machine.memory[0x300] == 3

    def test_LD_I_VX(self):
        self.machine.register_i = 0x300
        for index in range(0xf):
            self.machine.v[index] = index
        self.machine.decode_instruction(0xff55)  # memory at I is set to values in V0 - VF
        for index in range(0xf):
            assert self.machine.memory[0x300 + index] == index

    def test_LD_VX_I(self):
        self.machine.register_i = 0x300
        for index in range(0xf):
            self.machine.memory[0x300 + index] = index
        self.machine.decode_instruction(0xff65)  # V0 - VF is set to memory at I
        for index in range(0xf):
            assert self.machine.v[index] == index


