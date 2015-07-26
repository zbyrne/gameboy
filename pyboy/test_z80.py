from unittest import TestCase
from z80 import add_8bit, add_16bit, sub_8bit, sub_16bit
from z80 import rotate_right, rotate_right_through_carry


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

    def test_8bit_sub_carry_set(self):
        res = sub_8bit(0xF0, 0x10)
        self.assertEqual(res.result, 0xE0)
        self.assertTrue(res.c_flag)

    def test_8bit_sub_carry_clear(self):
        res = sub_8bit(0xE0, 0xF0)
        self.assertEqual(res.result, 0xF0)
        self.assertFalse(res.c_flag)

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
        self.assertTrue(res.c_flag)
        self.assertTrue(res.h_flag)
        self.assertTrue(res.z_flag)

    def test_8bit_sub_with_carry_flags_clear(self):
        res = sub_8bit(0xF0, 0xF0, c=1)
        self.assertEqual(res.result, 0xFF)
        self.assertFalse(res.c_flag)
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

    def test_16bit_sub_carry_set(self):
        res = sub_16bit(0xF000, 0x1000)
        self.assertEqual(res.result, 0xE000)
        self.assertTrue(res.c_flag)

    def test_16bit_sub_carry_clear(self):
        res = sub_16bit(0xE000, 0xF000)
        self.assertEqual(res.result, 0xF000)
        self.assertFalse(res.c_flag)

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
