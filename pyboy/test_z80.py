from unittest import TestCase
from z80 import Z80
from z80 import add_8bit, add_16bit, sub_8bit, sub_16bit
from z80 import rotate_right, rotate_right_through_carry
from z80 import rotate_left, rotate_left_through_carry
from z80 import ALUResult
from z80 import signed_8bit
from z80 import shift_left, shift_right_arithmetic, shift_right_logical
from z80 import swap
from z80 import bit, set_bit, reset_bit


class MockMem(dict):
    """
    Little Endian!
    """
    def read_byte(self, addr):
        x = self.get(addr, 0)
        self[addr] = x
        return x

    def write_byte(self, val, addr):
        self[addr] = val

    def read_word(self, addr):
        l = self.get(addr, 0)
        self[addr] = l
        h = self.get(addr + 1, 0)
        self[addr + 1] = h
        return (h << 8) + l

    def write_word(self, val, addr):
        self[addr] = val & 0xFF
        self[addr + 1] = (val >> 8) & 0xFF


class Z80Tests(TestCase):
    def test_dispatch(self):
        m = MockMem()
        m[0] = 0x4  # inc b
        z = Z80(m)
        cycles = z.dispatch()
        self.assertEqual(z.b, 1)
        self.assertEqual(z.pc, 1)
        self.assertEqual(cycles, 4)

    def test_set_flags(self):
        res1 = ALUResult(0, True, True, True, True)
        res2 = ALUResult(0, False, False, False, False)
        z = Z80(None)
        z.set_flags("znhc", res1)
        self.assertTrue(z.z_flag)
        self.assertTrue(z.n_flag)
        self.assertTrue(z.h_flag)
        self.assertTrue(z.c_flag)
        z.set_flags("znhc", res2)
        self.assertFalse(z.z_flag)
        self.assertFalse(z.n_flag)
        self.assertFalse(z.h_flag)
        self.assertFalse(z.c_flag)
        z.set_flags("zn", res1)
        self.assertTrue(z.z_flag)
        self.assertTrue(z.n_flag)
        self.assertFalse(z.h_flag)
        self.assertFalse(z.c_flag)

    def test_branching(self):
        m = MockMem()
        m[0] = 0x20 # jr nz 4
        m[1] = 0x4
        m[6] = 0x20
        m[7] = 0x0
        z = Z80(m)
        cycles = z.dispatch()
        self.assertEqual(cycles, 12)
        self.assertEqual(z.pc, 6)
        z.z_flag = True
        cycles = z.dispatch()
        self.assertEqual(cycles, 8)
        self.assertEqual(z.pc, 8)

    def test_daa(self):
        m = MockMem()
        m[0] = 0x27
        z = Z80(m)
        z.a = 0x3C
        cycles = z.dispatch()
        self.assertEqual(z.a, 0x42)

    def test_return(self):
        m = MockMem()
        m[0] = 0xC0 # ret_nz
        m[8] = 0x55
        m[9] = 0xAA
        z = Z80(m)
        z.sp = 8
        cycles = z.dispatch()
        self.assertEqual(cycles, 20)
        self.assertEqual(z.sp, 10)
        self.assertEqual(z.pc, 0xAA55)

    def test_push(self):
        m = MockMem()
        z = Z80(m)
        z.sp = 8
        z._push(0xAA55)
        self.assertEqual(z.sp, 6)
        self.assertEqual(m.read_word(6), 0xAA55)

    def test_pop(self):
        m = MockMem()
        m[8] = 0x55
        m[9] = 0xAA
        z = Z80(m)
        z.sp = 8
        val = z._pop()
        self.assertEqual(val, 0xAA55)
        self.assertEqual(z.sp, 0xA)

    def test_extra_ops(self):
        m = MockMem()
        m[0] = 0xCB # extra ops
        m[1] = 0x00 # rlc b
        z = Z80(m)
        z.b = 0x8
        cycles = z.dispatch()
        self.assertEqual(z.b, 0x10)
        self.assertEqual(z.pc, 2)


class Add8BitTests(TestCase):
    def test_8bit_add(self):
        res = add_8bit(4, 4)
        self.assertEqual(res.result, 8)
        self.assertFalse(res.n_flag)

    def test_8bit_add_carry_set(self):
        res = add_8bit(0xF0, 0x11)
        self.assertEqual(res.result, 1)
        self.assertTrue(res.c_flag)

    def test_8bit_add_carry_clear(self):
        res = add_8bit(0xE0, 0x10)
        self.assertEqual(res.result, 0xF0)
        self.assertFalse(res.c_flag)

    def test_8bit_add_half_set(self):
        res = add_8bit(0xF, 1)
        self.assertEqual(res.result, 0x10)
        self.assertTrue(res.h_flag)

    def test_8bit_add_half_clear(self):
        res = add_8bit(0xE, 1)
        self.assertEqual(res.result, 0xF)
        self.assertFalse(res.h_flag)

    def test_8bit_add_zero(self):
        res = add_8bit(0, 0)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)

    def test_8bit_add_with_carry_flags_set(self):
        res = add_8bit(0xF8, 0x7, c=1)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.c_flag)
        self.assertTrue(res.h_flag)
        self.assertTrue(res.z_flag)

    def test_8bit_add_with_carry_flags_clear(self):
        res = add_8bit(0xF0, 0x1, c=1)
        self.assertEqual(res.result, 0xF2)
        self.assertFalse(res.c_flag)
        self.assertFalse(res.h_flag)
        self.assertFalse(res.z_flag)


class Sub8BitTests(TestCase):
    def test_8bit_sub(self):
        res = sub_8bit(8, 4)
        self.assertEqual(res.result, 4)
        self.assertTrue(res.n_flag)

    def test_8bit_sub_carry_clear(self):
        res = sub_8bit(0xF0, 0x10)
        self.assertEqual(res.result, 0xE0)
        self.assertFalse(res.c_flag)

    def test_8bit_sub_carry_set(self):
        res = sub_8bit(0xE0, 0xF0)
        self.assertEqual(res.result, 0xF0)
        self.assertTrue(res.c_flag)

    def test_8bit_sub_half_set(self):
        res = sub_8bit(0xF, 0x1)
        self.assertEqual(res.result, 0xE)
        self.assertTrue(res.h_flag)

    def test_8bit_sub_half_clear(self):
        res = sub_8bit(0xE, 0xF)
        self.assertEqual(res.result, 0xFF)
        self.assertFalse(res.h_flag)

    def test_8bit_sub_zero(self):
        res = sub_8bit(0xF, 0xF)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)

    def test_8bit_sub_with_carry_flags_set(self):
        res = sub_8bit(0xF, 0xE, c=1)
        self.assertEqual(res.result, 0)
        self.assertFalse(res.c_flag)
        self.assertTrue(res.h_flag)
        self.assertTrue(res.z_flag)

    def test_8bit_sub_with_carry_flags_clear(self):
        res = sub_8bit(0xF0, 0xF0, c=1)
        self.assertEqual(res.result, 0xFF)
        self.assertTrue(res.c_flag)
        self.assertFalse(res.h_flag)
        self.assertFalse(res.z_flag)


class Add16BitTests(TestCase):
    def test_16bit_add(self):
        res = add_16bit(4, 4)
        self.assertEqual(res.result, 8)
        self.assertFalse(res.n_flag)

    def test_16bit_add_carry(self):
        res = add_16bit(0xF000, 0x1100)
        self.assertEqual(res.result, 0x100)
        self.assertTrue(res.c_flag)
        self.assertFalse(res.h_flag)
        self.assertFalse(res.z_flag)

    def test_16bit_add_half(self):
        res = add_16bit(0xF00, 0x100)
        self.assertEqual(res.result, 0x1000)
        self.assertTrue(res.h_flag)
        self.assertFalse(res.c_flag)
        self.assertFalse(res.z_flag)

    def test_16bit_add_zero(self):
        res = add_16bit(0, 0)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)
        self.assertFalse(res.c_flag)
        self.assertFalse(res.h_flag)


class Sub16BitTests(TestCase):
    def test_16bit_sub(self):
        res = sub_16bit(8, 4)
        self.assertEqual(res.result, 4)
        self.assertTrue(res.n_flag)

    def test_16bit_sub_carry_clear(self):
        res = sub_16bit(0xF000, 0x1000)
        self.assertEqual(res.result, 0xE000)
        self.assertFalse(res.c_flag)

    def test_16bit_sub_carry_set(self):
        res = sub_16bit(0xE000, 0xF000)
        self.assertEqual(res.result, 0xF000)
        self.assertTrue(res.c_flag)

    def test_16bit_sub_half_set(self):
        res = sub_16bit(0xF00, 0x100)
        self.assertEqual(res.result, 0xE00)
        self.assertTrue(res.h_flag)

    def test_16bit_sub_half_clear(self):
        res = sub_16bit(0xE00, 0xF00)
        self.assertEqual(res.result, 0xFF00)
        self.assertFalse(res.h_flag)

    def test_16bit_sub_zero(self):
        res = sub_16bit(0xF00, 0xF00)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)


class RotateRightTests(TestCase):
    def test_rotate_right(self):
        res = rotate_right(0x10)
        self.assertEqual(res.result, 0x8)
        self.assertFalse(res.n_flag)
        self.assertFalse(res.h_flag)

    def test_rotate_right_wrap(self):
        res = rotate_right(1)
        self.assertEqual(res.result, 0x80)
        self.assertTrue(res.c_flag)

    def test_rotate_right_zero(self):
        res = rotate_right(0)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)

    def test_rotate_right_through_carry(self):
        res = rotate_right_through_carry(0x10)
        self.assertEqual(res.result, 0x8)
        self.assertFalse(res.n_flag)
        self.assertFalse(res.h_flag)

    def test_rotate_right_through_carry_with_carry(self):
        res = rotate_right_through_carry(0x10, c=1)
        self.assertEqual(res.result, 0x88)
        self.assertFalse(res.c_flag)

    def test_rotate_right_through_carry_set_carry(self):
        res = rotate_right_through_carry(1)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.c_flag)
        self.assertTrue(res.z_flag)


class RotateLeftTests(TestCase):
    def test_rotate_left(self):
        res = rotate_left(0x8)
        self.assertEqual(res.result, 0x10)
        self.assertFalse(res.n_flag)
        self.assertFalse(res.h_flag)

    def test_rotate_left_wraps(self):
        res = rotate_left(0x80)
        self.assertEqual(res.result, 0x1)
        self.assertTrue(res.c_flag)

    def test_rotate_left_zero(self):
        res = rotate_left(0)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)

    def test_rotate_left_through_carry(self):
        res = rotate_left_through_carry(0x8)
        self.assertEqual(res.result, 0x10)
        self.assertFalse(res.n_flag)
        self.assertFalse(res.h_flag)

    def test_rotate_left_through_carry_with_carry(self):
        res = rotate_left_through_carry(0x8, c=1)
        self.assertEqual(res.result, 0x11)
        self.assertFalse(res.c_flag)

    def test_rotate_left_through_carry_set_carry(self):
        res = rotate_left_through_carry(0x80)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.c_flag)
        self.assertTrue(res.z_flag)


class Signed8BitTests(TestCase):
    def test_positive(self):
        res = signed_8bit(1)
        self.assertEqual(res, 1)

    def test_negative(self):
        res = signed_8bit(0xFF)
        self.assertEqual(res, -1)


class ShiftLeftTests(TestCase):
    def test_shift_left(self):
        res = shift_left(0x8)
        self.assertEqual(res.result, 0x10)
        self.assertFalse(res.n_flag)
        self.assertFalse(res.h_flag)

    def test_shift_left_zero(self):
        res = shift_left(0)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)

    def test_shift_left_carry(self):
        res = shift_left(0x80)
        self.assertEqual(res.result, 0)
        self.assertTrue(res.z_flag)
        self.assertTrue(res.c_flag)


class ShiftRightTests(TestCase):
    def test_shift_right_arithmetic(self):
        res = shift_right_arithmetic(0x81)
        self.assertEqual(res.result, 0xC0)
        self.assertTrue(res.c_flag)

    def test_shift_right_logical(self):
        res = shift_right_logical(0x81)
        self.assertEqual(res.result, 0x40)
        self.assertTrue(res.c_flag)


class SwapTests(TestCase):
    def test_swap(self):
        res = swap(0xA5)
        self.assertEqual(res.result, 0x5A)


class BitTests(TestCase):
    def test_bit(self):
        res = bit(0x5, 2)
        self.assertFalse(res.z_flag)
        res = bit(0x5, 3)
        self.assertTrue(res.z_flag)

    def test_reset_bit(self):
        res = reset_bit(0x5, 2)
        self.assertEqual(res.result, 0x1)
        res = reset_bit(0x5, 3)
        self.assertEqual(res.result, 0x5)

    def test_set_bit(self):
        res = set_bit(0x5, 2)
        self.assertEqual(res.result, 0x5)
        res = set_bit(0x5, 3)
        self.assertEqual(res.result, 0xD)
