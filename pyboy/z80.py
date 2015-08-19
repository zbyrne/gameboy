from collections import namedtuple
from functools import wraps


Z_FLAG = 1 << 7
N_FLAG = 1 << 6
H_FLAG = 1 << 5
C_FLAG = 1 << 4


def op_code(code, cycles, branch_cycles=0):
    """
    Decorator for methods of Z80 that implement instructions.  Causes
    the method to return the number of clock cycles
    consumed. Instructions that branch should return something truthy
    and pass branch cycles to the decorator.
    """
    def dec(fn):
        setattr(fn, "op_code", code)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            branch = fn(*args, **kwargs)
            return cycles if not branch else branch_cycles
        return wrapper
    return dec


def extra_op(code):
    """
    The instruction 0xCB calls a table of 256 extra instructions.
    """
    def dec(fn):
        setattr(fn, "extra_op", code)
        return fn
    return dec


class Z80(object):

    def __init__(self, mem):
        self._mem = mem
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0
        self.h = 0
        self.l = 0
        self.sp = 0
        self.pc = 0
        self.op_map = {}
        self.extra_ops_map = {}
        for attr in dir(self):
            attr = getattr(self, attr)
            if hasattr(attr, "op_code"):
                self.op_map[attr.op_code] = attr
            if hasattr(attr, "extra_op"):
                self.extra_ops_map[attr.extra_op] = attr

    def dispatch(self):
        instruction = self._mem.read_byte(self.pc)
        return self.op_map[instruction]()

    @property
    def af(self):
        return (self.a << 8) + self.f

    @af.setter
    def af(self, val):
        self.a = (val >> 8) & 0xFF
        self.f = val & 0xFF

    @property
    def bc(self):
        return (self.b << 8) + self.c

    @bc.setter
    def bc(self, val):
        self.b = (val >> 8) & 0xFF
        self.c = val & 0xFF

    @property
    def de(self):
        return (self.d << 8) + self.e

    @de.setter
    def de(self, val):
        self.d = (val >> 8) & 0xFF
        self.e = val & 0xFF

    @property
    def hl(self):
        return (self.h << 8) + self.l

    @hl.setter
    def hl(self, val):
        self.h = (val >> 8) & 0xFF
        self.l = val & 0xFF

    @property
    def z_flag(self):
        return bool(self.f & Z_FLAG)

    @z_flag.setter
    def z_flag(self, val):
        if val:
            self.f |= Z_FLAG
        else:
            self.f &= ~Z_FLAG

    @property
    def n_flag(self):
        return bool(self.f & N_FLAG)

    @n_flag.setter
    def n_flag(self, val):
        if val:
            self.f |= N_FLAG
        else:
            self.f &= ~N_FLAG

    @property
    def h_flag(self):
        return bool(self.f & H_FLAG)

    @h_flag.setter
    def h_flag(self, val):
        if val:
            self.f |= H_FLAG
        else:
            self.f &= ~H_FLAG

    @property
    def c_flag(self):
        return bool(self.f & C_FLAG)

    @c_flag.setter
    def c_flag(self, val):
        if val:
            self.f |= C_FLAG
        else:
            self.f &= ~C_FLAG

    def set_flags(self, flag_str, result):
        """
        Pass in a format string that looks like "znhc" and an
        ALUResult and the appropriate flags will be copied into the f
        register. Yes, this is stringly typed.
        """
        if "z" in flag_str:
            self.z_flag = result.z_flag
        if "n" in flag_str:
            self.n_flag = result.n_flag
        if "h" in flag_str:
            self.h_flag = result.h_flag
        if "c" in flag_str:
            self.c_flag = result.c_flag

    def _push(self, val):
        self.sp -= 2
        self._mem.write_word(val, self.sp)

    def _pop(self):
        val = self._mem.read_word(self.sp)
        self.sp +=2
        return val

    # Instructions
    # Each instruction is responsible for updating PC.
    # This is to make branching simpler.

    @op_code(0x0, 4)
    def nop(self):
        self.pc += 1

    @op_code(0x1, 12)
    def ld_bc_d16(self):
        self.pc += 1
        self.bc = self._mem.read_word(self.pc)
        self.pc += 2

    @op_code(0x2, 8)
    def ld_addr_bc_a(self):
        self._mem.write_byte(self.a, self.bc)
        self.pc +=1

    @op_code(0x3, 8)
    def inc_bc(self):
        self.pc += 1
        self.bc = add_16bit(self.bc, 1).result

    @op_code(0x4, 4)
    def inc_b(self):
        self.pc += 1
        res = add_8bit(self.b, 1)
        self.set_flags("znh", res)
        self.b = res.result

    @op_code(0x5, 4)
    def dec_b(self):
        self.pc += 1
        res = sub_8bit(self.b, 1)
        self.set_flags("znh", res)
        self.b = res.result

    @op_code(0x6, 8)
    def ld_b_d8(self):
        self.pc += 1
        self.b = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0x7, 4)
    def rlca(self):
        self.pc +=1
        res = rotate_left(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8, 20)
    def ld_a16_sp(self):
        self.pc +=1
        addr = self._mem.read_word(self.pc)
        self.pc += 2
        self._mem.write_word(self.sp, addr)

    @op_code(0x9, 8)
    def add_hl_bc(self):
        self.pc += 1
        res = add_16bit(self.hl, self.bc)
        self.set_flags("nhc", res)
        self.hl = res.result

    @op_code(0xA, 8)
    def ld_a_addr_bc(self):
        self.pc += 1
        self.a = self._mem.read_byte(self.bc)

    @op_code(0xB, 8)
    def dec_bc(self):
        self.pc += 1
        self.bc = sub_16bit(self.bc, 1).result

    @op_code(0xC, 4)
    def inc_c(self):
        self.pc += 1
        res = add_8bit(self.c, 1)
        self.set_flags("znh", res)
        self.c = res.result

    @op_code(0xD, 4)
    def dec_c(self):
        self.pc += 1
        res = sub_8bit(self.c, 1)
        self.set_flags("znh", res)
        self.c = res.result

    @op_code(0xE, 8)
    def ld_c_d8(self):
        self.pc += 1
        self.c = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0xF, 4)
    def rrca(self):
        self.pc +=1
        res = rotate_right(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x10, 4)
    def stop(self):
        """
        Going to have to do something silly here to stop the cpu.
        """
        self.pc += 2

    @op_code(0x11, 12)
    def ld_de_d16(self):
        self.pc += 1
        self.de = self._mem.read_word(self.pc)
        self.pc += 2

    @op_code(0x12, 8)
    def ld_addr_de_a(self):
        self._mem.write_byte(self.a, self.de)
        self.pc +=1

    @op_code(0x13, 8)
    def inc_de(self):
        self.pc += 1
        self.de = add_16bit(self.de, 1).result

    @op_code(0x14, 4)
    def inc_d(self):
        self.pc += 1
        res = add_8bit(self.d, 1)
        self.set_flags("znh", res)
        self.d = res.result

    @op_code(0x15, 4)
    def dec_d(self):
        self.pc += 1
        res = sub_8bit(self.d, 1)
        self.set_flags("znh", res)
        self.d = res.result

    @op_code(0x16, 8)
    def ld_d_d8(self):
        self.pc += 1
        self.d = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0x17, 4)
    def rla(self):
        self.pc +=1
        res = rotate_left_through_carry(self.a, int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x18, 12)
    def jr_r8(self):
        self.pc += 2
        offset = signed_8bit(self._mem.read_byte(self.pc - 1))
        self.pc += offset

    @op_code(0x19, 8)
    def add_hl_de(self):
        self.pc += 1
        res = add_16bit(self.hl, self.de)
        self.set_flags("nhc", res)
        self.hl = res.result

    @op_code(0x1A, 8)
    def ld_a_addr_de(self):
        self.pc += 1
        self.a = self._mem.read_byte(self.de)

    @op_code(0x1B, 8)
    def dec_de(self):
        self.pc += 1
        self.de = sub_16bit(self.de, 1).result

    @op_code(0x1C, 4)
    def inc_e(self):
        self.pc += 1
        res = add_8bit(self.e, 1)
        self.set_flags("znh", res)
        self.e = res.result

    @op_code(0x1D, 4)
    def dec_e(self):
        self.pc += 1
        res = sub_8bit(self.e, 1)
        self.set_flags("znh", res)
        self.e = res.result

    @op_code(0x1E, 8)
    def ld_e_d8(self):
        self.pc += 1
        self.e = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0x1F, 4)
    def rra(self):
        self.pc +=1
        res = rotate_right_through_carry(self.a, int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x20, 8, branch_cycles=12)
    def jr_nz_r8(self):
        self.pc += 2
        offset = signed_8bit(self._mem.read_byte(self.pc - 1))
        if not self.z_flag:
            self.pc += offset
            return True

    @op_code(0x21, 12)
    def ld_hl_d16(self):
        self.pc += 1
        self.hl = self._mem.read_word(self.pc)
        self.pc += 2

    @op_code(0x22, 8)
    def ld_addr_hl_inc_a(self):
        self.pc +=1
        self._mem.write_byte(self.a, self.hl)
        self.hl = add_16bit(self.hl, 1).result

    @op_code(0x23, 8)
    def inc_hl(self):
        self.pc += 1
        self.hl = add_16bit(self.hl, 1).result

    @op_code(0x24, 4)
    def inc_h(self):
        self.pc += 1
        res = add_8bit(self.h, 1)
        self.set_flags("znh", res)
        self.h = res.result

    @op_code(0x25, 4)
    def dec_h(self):
        self.pc += 1
        res = sub_8bit(self.h, 1)
        self.set_flags("znh", res)
        self.h = res.result

    @op_code(0x26, 8)
    def ld_h_d8(self):
        self.pc += 1
        self.h = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0x27, 4)
    def daa(self):
        """
        This instruction makes an adjustment to correct the
        accumulator after mathing two BCD values. There will be bugs
        here. Might have to generate a lookup table just to be sure.
        """
        self.pc += 1
        val = 0
        if self.a & 0xF > 0x9 or self.h_flag:
            val += 0x6
        if self.a & 0xF0 > 0x90 or self.c_flag:
            val += 0x60
        if self.n_flag:
            val = (-val) & 0xFF
        res = add_8bit(self.a, val)
        self.h_flag = False
        self.z_flag = res.result == 0
        self.c_flag = self.c_flag or res.c_flag
        self.a = res.result

    @op_code(0x28, 8, branch_cycles=12)
    def jr_z_r8(self):
        self.pc += 2
        offset = signed_8bit(self._mem.read_byte(self.pc - 1))
        if self.z_flag:
            self.pc += offset
            return True

    @op_code(0x29, 8)
    def add_hl_hl(self):
        self.pc += 1
        res = add_16bit(self.hl, self.hl)
        self.set_flags("nhc", res)
        self.hl = res.result

    @op_code(0x2A, 8)
    def ld_a_addr_hl_inc(self):
        self.pc += 1
        self.a = self._mem.read_byte(self.hl)
        self.hl = add_16bit(self.hl, 1).result

    @op_code(0x2B, 8)
    def dec_hl(self):
        self.pc += 1
        self.hl = sub_16bit(self.hl, 1).result

    @op_code(0x2C, 4)
    def inc_l(self):
        self.pc += 1
        res = add_8bit(self.l, 1)
        self.set_flags("znh", res)
        self.l = res.result

    @op_code(0x2D, 4)
    def dec_l(self):
        self.pc += 1
        res = sub_8bit(self.l, 1)
        self.set_flags("znh", res)
        self.l = res.result

    @op_code(0x2E, 8)
    def ld_l_d8(self):
        self.pc += 1
        self.l = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0x2F, 4)
    def cpl(self):
        self.pc += 1
        self.n_flag = True
        self.h_flag = True
        self.a = self.a ^ 0xFF

    @op_code(0x30, 8, branch_cycles=12)
    def jr_nc_r8(self):
        self.pc += 2
        offset = signed_8bit(self._mem.read_byte(self.pc - 1))
        if not self.c_flag:
            self.pc += offset
            return True

    @op_code(0x31, 12)
    def ld_sp_d16(self):
        self.pc += 1
        self.sp = self._mem.read_word(self.pc)
        self.pc += 2

    @op_code(0x32, 8)
    def ld_addr_hl_dec_a(self):
        self.pc +=1
        self._mem.write_byte(self.a, self.hl)
        self.hl = sub_16bit(self.hl, 1).result

    @op_code(0x33, 8)
    def inc_sp(self):
        self.pc += 1
        self.sp = add_16bit(self.sp, 1).result

    @op_code(0x34, 12)
    def inc_addr_hl(self):
        self.pc += 1
        val = self._mem.read_byte(self.hl)
        res = add_8bit(val, 1)
        self.set_flags("znh", res)
        self._mem.write_byte(res.result, self.hl)

    @op_code(0x35, 4)
    def dec_addr_hl(self):
        self.pc += 1
        val = self._mem.read_byte(self.hl)
        res = sub_8bit(val, 1)
        self.set_flags("znh", res)
        self._mem.write_byte(res.result, self.hl)

    @op_code(0x36, 12)
    def ld_addr_hl_d8(self):
        self.pc += 1
        val = self._mem.read_byte(self.pc)
        self.pc += 1
        self._mem.write_byte(val, self.hl)

    @op_code(0x37, 4)
    def scf(self):
        self.pc += 1
        self.n_flag = False
        self.h_flag = False
        self.c_flag = True

    @op_code(0x38, 8, branch_cycles=12)
    def jr_c_r8(self):
        self.pc += 2
        offset = signed_8bit(self._mem.read_byte(self.pc - 1))
        if self.c_flag:
            self.pc += offset
            return True

    @op_code(0x39, 8)
    def add_hl_sp(self):
        self.pc += 1
        res = add_16bit(self.hl, self.sp)
        self.set_flags("nhc", res)
        self.hl = res.result

    @op_code(0x3A, 8)
    def ld_a_addr_hl_dec(self):
        self.pc += 1
        self.a = self._mem.read_byte(self.hl)
        self.hl = sub_16bit(self.hl, 1).result

    @op_code(0x3B, 8)
    def dec_sp(self):
        self.pc += 1
        self.sp = sub_16bit(self.sp, 1).result

    @op_code(0x3C, 4)
    def inc_a(self):
        self.pc += 1
        res = add_8bit(self.a, 1)
        self.set_flags("znh", res)
        self.a = res.result

    @op_code(0x3D, 4)
    def dec_a(self):
        self.pc += 1
        res = sub_8bit(self.a, 1)
        self.set_flags("znh", res)
        self.a = res.result

    @op_code(0x3E, 8)
    def ld_a_d8(self):
        self.pc += 1
        self.a = self._mem.read_byte(self.pc)
        self.pc += 1

    @op_code(0x3F, 4)
    def ccf(self):
        self.pc += 1
        self.n_flag = False
        self.h_flag = False
        self.c_flag = not self.c_flag

    @op_code(0x40, 4)
    def ld_b_b(self):
        self.pc += 1
        self.b = self.b

    @op_code(0x41, 4)
    def ld_b_c(self):
        self.pc += 1
        self.b = self.c

    @op_code(0x42, 4)
    def ld_b_d(self):
        self.pc += 1
        self.b = self.d

    @op_code(0x43, 4)
    def ld_b_e(self):
        self.pc += 1
        self.b = self.e

    @op_code(0x44, 4)
    def ld_b_h(self):
        self.pc += 1
        self.b = self.h

    @op_code(0x45, 4)
    def ld_b_l(self):
        self.pc += 1
        self.b = self.l

    @op_code(0x46, 8)
    def ld_b_addr_hl(self):
        self.pc += 1
        self.b = self._mem.read_byte(self.hl)

    @op_code(0x47, 4)
    def ld_b_a(self):
        self.pc += 1
        self.b = self.a

    @op_code(0x48, 4)
    def ld_c_b(self):
        self.pc += 1
        self.c = self.b

    @op_code(0x49, 4)
    def ld_c_c(self):
        self.pc += 1
        self.c = self.c

    @op_code(0x4A, 4)
    def ld_c_d(self):
        self.pc += 1
        self.c = self.d

    @op_code(0x4B, 4)
    def ld_c_e(self):
        self.pc += 1
        self.c = self.e

    @op_code(0x4C, 4)
    def ld_c_h(self):
        self.pc += 1
        self.c = self.h

    @op_code(0x4D, 4)
    def ld_c_l(self):
        self.pc += 1
        self.c = self.l

    @op_code(0x4E, 8)
    def ld_c_addr_hl(self):
        self.pc += 1
        self.c = self._mem.read_byte(self.hl)

    @op_code(0x4F, 4)
    def ld_c_a(self):
        self.pc += 1
        self.c = self.a

    @op_code(0x50, 4)
    def ld_d_b(self):
        self.pc += 1
        self.d = self.b

    @op_code(0x51, 4)
    def ld_d_c(self):
        self.pc += 1
        self.d = self.c

    @op_code(0x52, 4)
    def ld_d_d(self):
        self.pc += 1
        self.d = self.d

    @op_code(0x53, 4)
    def ld_d_e(self):
        self.pc += 1
        self.d = self.e

    @op_code(0x54, 4)
    def ld_d_h(self):
        self.pc += 1
        self.d = self.h

    @op_code(0x55, 4)
    def ld_d_l(self):
        self.pc += 1
        self.d = self.l

    @op_code(0x56, 8)
    def ld_d_addr_hl(self):
        self.pc += 1
        self.d = self._mem.read_byte(self.hl)

    @op_code(0x57, 4)
    def ld_d_a(self):
        self.pc += 1
        self.d = self.a

    @op_code(0x58, 4)
    def ld_e_b(self):
        self.pc += 1
        self.e = self.b

    @op_code(0x59, 4)
    def ld_e_c(self):
        self.pc += 1
        self.e = self.c

    @op_code(0x5A, 4)
    def ld_e_d(self):
        self.pc += 1
        self.e = self.d

    @op_code(0x5B, 4)
    def ld_e_e(self):
        self.pc += 1
        self.e = self.e

    @op_code(0x5C, 4)
    def ld_e_h(self):
        self.pc += 1
        self.e = self.h

    @op_code(0x5D, 4)
    def ld_e_l(self):
        self.pc += 1
        self.e = self.l

    @op_code(0x5E, 8)
    def ld_e_addr_hl(self):
        self.pc += 1
        self.e = self._mem.read_byte(self.hl)

    @op_code(0x5F, 4)
    def ld_e_a(self):
        self.pc += 1
        self.e = self.a

    @op_code(0x60, 4)
    def ld_h_b(self):
        self.pc += 1
        self.h = self.b

    @op_code(0x61, 4)
    def ld_h_c(self):
        self.pc += 1
        self.h = self.c

    @op_code(0x62, 4)
    def ld_h_d(self):
        self.pc += 1
        self.h = self.d

    @op_code(0x63, 4)
    def ld_h_e(self):
        self.pc += 1
        self.h = self.e

    @op_code(0x64, 4)
    def ld_h_h(self):
        self.pc += 1
        self.h = self.h

    @op_code(0x65, 4)
    def ld_h_l(self):
        self.pc += 1
        self.h = self.l

    @op_code(0x66, 8)
    def ld_h_addr_hl(self):
        self.pc += 1
        self.h = self._mem.read_byte(self.hl)

    @op_code(0x67, 4)
    def ld_h_a(self):
        self.pc += 1
        self.h = self.a

    @op_code(0x68, 4)
    def ld_l_b(self):
        self.pc += 1
        self.l = self.b

    @op_code(0x69, 4)
    def ld_l_c(self):
        self.pc += 1
        self.l = self.c

    @op_code(0x6A, 4)
    def ld_l_d(self):
        self.pc += 1
        self.l = self.d

    @op_code(0x6B, 4)
    def ld_l_e(self):
        self.pc += 1
        self.l = self.e

    @op_code(0x6C, 4)
    def ld_l_h(self):
        self.pc += 1
        self.l = self.h

    @op_code(0x6D, 4)
    def ld_l_l(self):
        self.pc += 1
        self.l = self.l

    @op_code(0x6E, 8)
    def ld_l_addr_hl(self):
        self.pc += 1
        self.l = self._mem.read_byte(self.hl)

    @op_code(0x6F, 4)
    def ld_l_a(self):
        self.pc += 1
        self.l = self.a

    @op_code(0x70, 8)
    def ld_addr_hl_b(self):
        self.pc += 1
        self._mem.write_byte(self.b, self.hl)

    @op_code(0x71, 8)
    def ld_addr_hl_c(self):
        self.pc += 1
        self._mem.write_byte(self.c, self.hl)

    @op_code(0x72, 8)
    def ld_addr_hl_d(self):
        self.pc += 1
        self._mem.write_byte(self.d, self.hl)

    @op_code(0x73, 8)
    def ld_addr_hl_e(self):
        self.pc += 1
        self._mem.write_byte(self.e, self.hl)

    @op_code(0x74, 8)
    def ld_addr_hl_h(self):
        self.pc += 1
        self._mem.write_byte(self.h, self.hl)

    @op_code(0x75, 8)
    def ld_addr_hl_l(self):
        self.pc += 1
        self._mem.write_byte(self.l, self.hl)

    @op_code(0x76, 4)
    def halt(self):
        self.pc += 1
        # do something silly to stop the cpu.

    @op_code(0x77, 8)
    def ld_addr_hl_a(self):
        self.pc += 1
        self._mem.write_byte(self.a, self.hl)

    @op_code(0x78, 4)
    def ld_a_b(self):
        self.pc += 1
        self.a = self.b

    @op_code(0x79, 4)
    def ld_a_c(self):
        self.pc += 1
        self.a = self.c

    @op_code(0x7A, 4)
    def ld_a_d(self):
        self.pc += 1
        self.a = self.d

    @op_code(0x7B, 4)
    def ld_a_e(self):
        self.pc += 1
        self.a = self.e

    @op_code(0x7C, 4)
    def ld_a_h(self):
        self.pc += 1
        self.a = self.h

    @op_code(0x7D, 4)
    def ld_a_l(self):
        self.pc += 1
        self.a = self.l

    @op_code(0x7E, 8)
    def ld_a_addr_hl(self):
        self.pc += 1
        self.a = self._mem.read_byte(self.hl)

    @op_code(0x7F, 4)
    def ld_a_a(self):
        self.pc += 1
        self.a = self.a

    @op_code(0x80, 4)
    def add_a_b(self):
        self.pc += 1
        res = add_8bit(self.a, self.b)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x81, 4)
    def add_a_c(self):
        self.pc += 1
        res = add_8bit(self.a, self.c)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x82, 4)
    def add_a_d(self):
        self.pc += 1
        res = add_8bit(self.a, self.d)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x83, 4)
    def add_a_e(self):
        self.pc += 1
        res = add_8bit(self.a, self.e)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x84, 4)
    def add_a_h(self):
        self.pc += 1
        res = add_8bit(self.a, self.h)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x85, 4)
    def add_a_l(self):
        self.pc += 1
        res = add_8bit(self.a, self.l)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x86, 8)
    def add_a_addr_hl(self):
        self.pc += 1
        res = add_8bit(self.a, self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x87, 4)
    def add_a_a(self):
        self.pc += 1
        res = add_8bit(self.a, self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x88, 4)
    def adc_a_b(self):
        self.pc += 1
        res = add_8bit(self.a, self.b, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x89, 4)
    def adc_a_c(self):
        self.pc += 1
        res = add_8bit(self.a, self.c, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8A, 4)
    def adc_a_d(self):
        self.pc += 1
        res = add_8bit(self.a, self.d, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8B, 4)
    def adc_a_e(self):
        self.pc += 1
        res = add_8bit(self.a, self.e, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8C, 4)
    def adc_a_h(self):
        self.pc += 1
        res = add_8bit(self.a, self.h, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8D, 4)
    def adc_a_l(self):
        self.pc += 1
        res = add_8bit(self.a, self.l, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8E, 8)
    def adc_a_addr_hl(self):
        self.pc += 1
        res = add_8bit(self.a, self._mem.read_byte(self.hl),
                       c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x8F, 4)
    def adc_a_a(self):
        self.pc += 1
        res = add_8bit(self.a, self.a, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x90, 4)
    def sub_b(self):
        self.pc += 1
        res = sub_8bit(self.a, self.b)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x91, 4)
    def sub_c(self):
        self.pc += 1
        res = sub_8bit(self.a, self.c)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x92, 4)
    def sub_d(self):
        self.pc += 1
        res = sub_8bit(self.a, self.d)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x93, 4)
    def sub_e(self):
        self.pc += 1
        res = sub_8bit(self.a, self.e)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x94, 4)
    def sub_h(self):
        self.pc += 1
        res = sub_8bit(self.a, self.h)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x95, 4)
    def sub_l(self):
        self.pc += 1
        res = sub_8bit(self.a, self.l)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x96, 8)
    def sub_addr_hl(self):
        self.pc += 1
        res = sub_8bit(self.a, self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x97, 4)
    def sub_a(self):
        self.pc += 1
        res = sub_8bit(self.a, self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x98, 4)
    def sbc_a_b(self):
        self.pc += 1
        res = sub_8bit(self.a, self.b, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x99, 4)
    def sbc_a_c(self):
        self.pc += 1
        res = sub_8bit(self.a, self.c, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x9A, 4)
    def sbc_a_d(self):
        self.pc += 1
        res = sub_8bit(self.a, self.d, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x9B, 4)
    def sbc_a_e(self):
        self.pc += 1
        res = sub_8bit(self.a, self.e, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x9C, 4)
    def sbc_a_h(self):
        self.pc += 1
        res = sub_8bit(self.a, self.h, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x9D, 4)
    def sbc_a_l(self):
        self.pc += 1
        res = sub_8bit(self.a, self.l, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x9E, 8)
    def sbc_a_addr_hl(self):
        self.pc += 1
        res = sub_8bit(self.a, self._mem.read_byte(self.hl),
                       c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0x9F, 4)
    def sbc_a_a(self):
        self.pc += 1
        res = sub_8bit(self.a, self.a, c = int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result

    @op_code(0xA0, 4)
    def and_b(self):
        self.pc += 1
        self.a &= self.b
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA1, 4)
    def and_c(self):
        self.pc += 1
        self.a &= self.c
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA2, 4)
    def and_d(self):
        self.pc += 1
        self.a &= self.d
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA3, 4)
    def and_e(self):
        self.pc += 1
        self.a &= self.e
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA4, 4)
    def and_h(self):
        self.pc += 1
        self.a &= self.h
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA5, 4)
    def and_l(self):
        self.pc += 1
        self.a &= self.l
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA6, 8)
    def and_addr_hl(self):
        self.pc += 1
        self.a &= self._mem.read_byte(self.hl)
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA7, 4)
    def and_a(self):
        self.pc += 1
        self.a &= self.a
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False

    @op_code(0xA8, 4)
    def xor_b(self):
        self.pc += 1
        self.a ^= self.b
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xA9, 4)
    def xor_c(self):
        self.pc += 1
        self.a ^= self.c
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xAA, 4)
    def xor_d(self):
        self.pc += 1
        self.a ^= self.d
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xAB, 4)
    def xor_e(self):
        self.pc += 1
        self.a ^= self.e
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xAC, 4)
    def xor_h(self):
        self.pc += 1
        self.a ^= self.h
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xAD, 4)
    def xor_l(self):
        self.pc += 1
        self.a ^= self.l
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xAE, 8)
    def xor_addr_hl(self):
        self.pc += 1
        self.a ^= self._mem.read_byte(self.hl)
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xAF, 4)
    def xor_a(self):
        self.pc += 1
        self.a ^= self.a
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB0, 4)
    def or_b(self):
        self.pc += 1
        self.a |= self.b
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB1, 4)
    def or_c(self):
        self.pc += 1
        self.a |= self.c
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB2, 4)
    def or_d(self):
        self.pc += 1
        self.a |= self.d
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB3, 4)
    def or_e(self):
        self.pc += 1
        self.a |= self.e
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB4, 4)
    def or_h(self):
        self.pc += 1
        self.a |= self.h
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB5, 4)
    def or_l(self):
        self.pc += 1
        self.a |= self.l
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB6, 8)
    def or_addr_hl(self):
        self.pc += 1
        self.a |= self._mem.read_byte(self.hl)
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB7, 4)
    def or_a(self):
        self.pc += 1
        self.a |= self.a
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False

    @op_code(0xB8, 4)
    def cp_b(self):
        self.pc += 1
        res = sub_8bit(self.a, self.b)
        self.set_flags("znhc", res)

    @op_code(0xB9, 4)
    def cp_c(self):
        self.pc += 1
        res = sub_8bit(self.a, self.c)
        self.set_flags("znhc", res)

    @op_code(0xBA, 4)
    def cp_d(self):
        self.pc += 1
        res = sub_8bit(self.a, self.d)
        self.set_flags("znhc", res)

    @op_code(0xBB, 4)
    def cp_e(self):
        self.pc += 1
        res = sub_8bit(self.a, self.e)
        self.set_flags("znhc", res)

    @op_code(0xBC, 4)
    def cp_h(self):
        self.pc += 1
        res = sub_8bit(self.a, self.h)
        self.set_flags("znhc", res)

    @op_code(0xBD, 4)
    def cp_l(self):
        self.pc += 1
        res = sub_8bit(self.a, self.l)
        self.set_flags("znhc", res)

    @op_code(0xBE, 8)
    def cp_addr_hl(self):
        self.pc += 1
        res = sub_8bit(self.a, self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)

    @op_code(0xBF, 4)
    def cp_a(self):
        self.pc += 1
        res = sub_8bit(self.a, self.a)
        self.set_flags("znhc", res)

    @op_code(0xC0, 8, branch_cycles=20)
    def ret_nz(self):
        if not self.z_flag:
            addr = self._pop()
            self.pc = addr
            return True
        self.pc +=1

    @op_code(0xC1, 12)
    def pop_bc(self):
        self.pc += 1
        self.bc = self._pop()

    @op_code(0xC2, 12, branch_cycles=16)
    def jp_nz_a16(self):
        if not self.z_flag:
            addr = self._mem.read_word(self.pc + 1)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xC3, 16)
    def jp_a16(self):
        addr = self._mem.read_word(self.pc + 1)
        self.pc = addr

    @op_code(0xC4, 12, branch_cycles=24)
    def call_nz_a16(self):
        if not self.z_flag:
            addr = self._mem.read_word(self.pc + 1)
            self._push(self.pc + 3)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xC5, 16)
    def push_bc(self):
        self.pc += 1
        self._push(self.bc)

    @op_code(0xC6, 8)
    def add_a_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        res = add_8bit(self.a, val)
        self.set_flags("znhc", res)
        self.a = res.result
        self.pc += 2

    @op_code(0xC7, 16)
    def rst_0x00(self):
        self._push(self.pc)
        self.pc = 0x00

    @op_code(0xC8, 8, branch_cycles=20)
    def ret_z(self):
        if self.z_flag:
            addr = self._pop()
            self.pc = addr
            return True
        self.pc +=1

    @op_code(0xC9, 16)
    def ret(self):
        addr = self._pop()
        self.pc = addr

    @op_code(0xCA, 12, branch_cycles=16)
    def jp_z_a16(self):
        if self.z_flag:
            addr = self._mem.read_word(self.pc + 1)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xCB, 8, branch_cycles=16)
    def extra_ops(self):
        op = self._mem.read_byte(self.pc + 1)
        self.pc += 2
        self.extra_ops_map[op]()
        # All extra ops take 8 cycles except the ones whose bottom 3
        # bits are 110 affecting the contents of (HL), which take
        # 16. So treat this like branching.
        return (op & 0x7) == 0x6

    @op_code(0xCC, 12, branch_cycles=24)
    def call_z_a16(self):
        if self.z_flag:
            addr = self._mem.read_word(self.pc + 1)
            self._push(self.pc + 3)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xCD, 24)
    def call_a16(self):
        addr = self._mem.read_word(self.pc + 1)
        self._push(self.pc + 3)
        self.pc = addr

    @op_code(0xCE, 8)
    def adc_a_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        res = add_8bit(self.a, val, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result
        self.pc += 2

    @op_code(0xCF, 16)
    def rst_0x08(self):
        self._push(self.pc)
        self.pc = 0x08

    @op_code(0xD0, 8, branch_cycles=20)
    def ret_nc(self):
        if not self.c_flag:
            addr = self._pop()
            self.pc = addr
            return True
        self.pc +=1

    @op_code(0xD1, 12)
    def pop_de(self):
        self.pc += 1
        self.de = self._pop()

    @op_code(0xD2, 12, branch_cycles=16)
    def jp_nc_a16(self):
        if not self.c_flag:
            addr = self._mem.read_word(self.pc + 1)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xD4, 12, branch_cycles=24)
    def call_nc_a16(self):
        if not self.c_flag:
            addr = self._mem.read_word(self.pc + 1)
            self._push(self.pc + 3)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xD5, 16)
    def push_de(self):
        self.pc += 1
        self._push(self.de)

    @op_code(0xD6, 8)
    def sub_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        res = sub_8bit(self.a, val)
        self.set_flags("znhc", res)
        self.a = res.result
        self.pc += 2

    @op_code(0xD7, 16)
    def rst_0x10(self):
        self._push(self.pc)
        self.pc = 0x10

    @op_code(0xD8, 8, branch_cycles=20)
    def ret_c(self):
        if self.c_flag:
            addr = self._pop()
            self.pc = addr
            return True
        self.pc +=1

    @op_code(0xD9, 16)
    def reti(self):
        # enable interrupts
        addr = self._pop()
        self.pc = addr

    @op_code(0xDA, 12, branch_cycles=16)
    def jp_c_a16(self):
        if self.c_flag:
            addr = self._mem.read_word(self.pc + 1)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xDC, 12, branch_cycles=24)
    def call_c_a16(self):
        if self.c_flag:
            addr = self._mem.read_word(self.pc + 1)
            self._push(self.pc + 3)
            self.pc = addr
            return True
        self.pc += 3

    @op_code(0xDE, 8)
    def sbc_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        res = sub_8bit(self.a, val, c=int(self.c_flag))
        self.set_flags("znhc", res)
        self.a = res.result
        self.pc += 2

    @op_code(0xDF, 16)
    def rst_0x18(self):
        self._push(self.pc)
        self.pc = 0x18

    @op_code(0xE0, 12)
    def ldh_a8_a(self):
        addr = 0xFF00 + self._mem.read_byte(self.pc + 1)
        self._mem.write_byte(self.a, addr)
        self.pc += 2

    @op_code(0xE1, 12)
    def pop_hl(self):
        self.pc += 1
        self.hl = self._pop()

    @op_code(0xE2, 8)
    def ld_addr_c_a(self):
        self._mem.write_byte(self.a, 0xFF00 + self.c)
        self.pc += 2

    @op_code(0xE5, 16)
    def push_hl(self):
        self.pc += 1
        self._push(self.hl)

    @op_code(0xE6, 8)
    def and_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        self.a &= val
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False
        self.pc += 2

    @op_code(0xE7, 16)
    def rst_0x20(self):
        self._push(self.pc)
        self.pc = 0x20

    @op_code(0xE8, 16)
    def add_sp_r8(self):
        val = signed_8bit(self._mem.read_byte(self.pc + 1))
        res = add_16bit(self.sp, val)
        self.set_flags("hc", res)
        self.z_flag = False
        self.n_flag = False
        self.sp = res.result
        self.pc += 2

    @op_code(0xE9, 4)
    def jp_addr_hl(self):
        addr = self._mem.read_word(self.hl)
        self.pc = addr

    @op_code(0xEA, 16)
    def ldh_a16_a(self):
        addr = self._mem.read_word(self.pc + 1)
        self._mem.write_byte(self.a, addr)
        self.pc += 3

    @op_code(0xEE, 8)
    def xor_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        self.a ^= val
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = False
        self.c_flag = False
        self.pc += 2

    @op_code(0xEF, 16)
    def rst_0x28(self):
        self._push(self.pc)
        self.pc = 0x28

    @op_code(0xF0, 12)
    def ldh_a_a8(self):
        addr = 0xFF00 + self._mem.read_byte(self.pc + 1)
        self.a = self._mem.read_byte(addr)
        self.pc += 2

    @op_code(0xF1, 12)
    def pop_AF(self):
        self.pc += 1
        self.af = self._pop()

    @op_code(0xF2, 8)
    def ld_a_addr_c(self):
        self.a = self._mem.read_byte(0xFF00 + self.c)
        self.pc += 2

    @op_code(0xF3, 4)
    def di(self):
        # disable interrupts
        self.pc += 1

    @op_code(0xF5, 16)
    def push_af(self):
        self.pc += 1
        self._push(self.af)

    @op_code(0xF6, 8)
    def or_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        self.a |= val
        self.z_flag = self.a == 0
        self.n_flag = False
        self.h_flag = True
        self.c_flag = False
        self.pc += 2

    @op_code(0xF7, 16)
    def rst_0x30(self):
        self._push(self.pc)
        self.pc = 0x30

    @op_code(0xF8, 12)
    def ld_hl_sp_r8(self):
        val = signed_8bit(self._mem.read_byte(self.pc + 1))
        self.hl = add_16bit(self.sp, val).result
        self.pc += 2

    @op_code(0xF9, 8)
    def ld_sp_hl(self):
        self.sp = self.hl
        self.pc += 1

    @op_code(0xFA, 16)
    def ldh_a_a16(self):
        addr = self._mem.read_word(self.pc + 1)
        self.a = self._mem.read_byte(addr)
        self.pc += 3

    @op_code(0xFB, 4)
    def ei(self):
        # enable interrupts
        self.pc += 1

    @op_code(0xFE, 8)
    def cp_d8(self):
        val = self._mem.read_byte(self.pc + 1)
        res = sub_8bit(self.a, val)
        self.set_flags("znhc", res)
        self.pc += 2

    @op_code(0xFF, 16)
    def rst_0x38(self):
        self._push(self.pc)
        self.pc = 0x38

    # Extra instructions
    # The 0xCB instruction took care of the PC and the clock
    # Just update registers/memory

    @extra_op(0x00)
    def rlc_b(self):
        res = rotate_left(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x01)
    def rlc_c(self):
        res = rotate_left(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x02)
    def rlc_d(self):
        res = rotate_left(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x03)
    def rlc_e(self):
        res = rotate_left(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x04)
    def rlc_h(self):
        res = rotate_left(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x05)
    def rlc_l(self):
        res = rotate_left(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x06)
    def rlc_addr_hl(self):
        res = rotate_left(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x07)
    def rlc_a(self):
        res = rotate_left(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x08)
    def rrc_b(self):
        res = rotate_right(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x09)
    def rrc_c(self):
        res = rotate_right(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x0A)
    def rrc_d(self):
        res = rotate_right(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x0B)
    def rrc_e(self):
        res = rotate_right(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x0C)
    def rrc_h(self):
        res = rotate_right(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x0D)
    def rrc_l(self):
        res = rotate_right(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x0E)
    def rrc_addr_hl(self):
        res = rotate_right(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x0F)
    def rrc_a(self):
        res = rotate_right(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x10)
    def rl_b(self):
        res = rotate_left_through_carry(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x11)
    def rl_c(self):
        res = rotate_left_through_carry(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x12)
    def rl_d(self):
        res = rotate_left_through_carry(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x13)
    def rl_e(self):
        res = rotate_left_through_carry(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x14)
    def rl_h(self):
        res = rotate_left_through_carry(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x15)
    def rl_l(self):
        res = rotate_left_through_carry(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x16)
    def rl_addr_hl(self):
        res = rotate_left_through_carry(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x17)
    def rl_a(self):
        res = rotate_left_through_carry(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x18)
    def rr_b(self):
        res = rotate_right_through_carry(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x19)
    def rr_c(self):
        res = rotate_right_through_carry(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x1A)
    def rr_d(self):
        res = rotate_right_through_carry(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x1B)
    def rr_e(self):
        res = rotate_right_through_carry(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x1C)
    def rr_h(self):
        res = rotate_right_through_carry(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x1D)
    def rr_l(self):
        res = rotate_right_through_carry(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x1E)
    def rr_addr_hl(self):
        res = rotate_right_through_carry(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x1F)
    def rr_a(self):
        res = rotate_right_through_carry(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x20)
    def sla_b(self):
        res = shift_left(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x21)
    def sla_c(self):
        res = shift_left(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x22)
    def sla_d(self):
        res = shift_left(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x23)
    def sla_e(self):
        res = shift_left(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x24)
    def sla_h(self):
        res = shift_left(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x25)
    def sla_l(self):
        res = shift_left(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x26)
    def sla_addr_hl(self):
        res = shift_left(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x27)
    def sla_a(self):
        res = shift_left(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x28)
    def sra_b(self):
        res = shift_right_arithmetic(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x29)
    def sra_c(self):
        res = shift_right_arithmetic(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x2A)
    def sra_d(self):
        res = shift_right_arithmetic(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x2B)
    def sra_e(self):
        res = shift_right_arithmetic(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x2C)
    def sra_h(self):
        res = shift_right_arithmetic(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x2D)
    def sra_l(self):
        res = shift_right_arithmetic(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x2E)
    def sra_addr_hl(self):
        res = shift_right_arithmetic(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x2F)
    def sra_a(self):
        res = shift_right_arithmetic(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x30)
    def swap_b(self):
        res = swap(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x31)
    def swap_c(self):
        res = swap(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x32)
    def swap_d(self):
        res = swap(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x33)
    def swap_e(self):
        res = swap(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x34)
    def swap_h(self):
        res = swap(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x35)
    def swap_l(self):
        res = swap(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x36)
    def swap_addr_hl(self):
        res = swap(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x37)
    def swap_a(self):
        res = swap(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x38)
    def srl_b(self):
        res = shift_right_logical(self.b)
        self.set_flags("znhc", res)
        self.b = res.result

    @extra_op(0x39)
    def srl_c(self):
        res = shift_right_logical(self.c)
        self.set_flags("znhc", res)
        self.c = res.result

    @extra_op(0x3A)
    def srl_d(self):
        res = shift_right_logical(self.d)
        self.set_flags("znhc", res)
        self.d = res.result

    @extra_op(0x3B)
    def srl_e(self):
        res = shift_right_logical(self.e)
        self.set_flags("znhc", res)
        self.e = res.result

    @extra_op(0x3C)
    def srl_h(self):
        res = shift_right_logical(self.h)
        self.set_flags("znhc", res)
        self.h = res.result

    @extra_op(0x3D)
    def srl_l(self):
        res = shift_right_logical(self.l)
        self.set_flags("znhc", res)
        self.l = res.result

    @extra_op(0x3E)
    def srl_addr_hl(self):
        res = shift_right_logical(self._mem.read_byte(self.hl))
        self.set_flags("znhc", res)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x3F)
    def srl_a(self):
        res = shift_right_logical(self.a)
        self.set_flags("znhc", res)
        self.a = res.result

    @extra_op(0x40)
    def bit_0_b(self):
        self.set_flags("znh", bit(self.b, 0))

    @extra_op(0x41)
    def bit_0_c(self):
        self.set_flags("znh", bit(self.c, 0))

    @extra_op(0x42)
    def bit_0_d(self):
        self.set_flags("znh", bit(self.d, 0))

    @extra_op(0x43)
    def bit_0_e(self):
        self.set_flags("znh", bit(self.e, 0))

    @extra_op(0x44)
    def bit_0_h(self):
        self.set_flags("znh", bit(self.h, 0))

    @extra_op(0x45)
    def bit_0_l(self):
        self.set_flags("znh", bit(self.l, 0))

    @extra_op(0x46)
    def bit_0_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 0))

    @extra_op(0x47)
    def bit_0_a(self):
        self.set_flags("znh", bit(self.a, 0))

    @extra_op(0x48)
    def bit_1_b(self):
        self.set_flags("znh", bit(self.b, 1))

    @extra_op(0x49)
    def bit_1_c(self):
        self.set_flags("znh", bit(self.c, 1))

    @extra_op(0x4A)
    def bit_1_d(self):
        self.set_flags("znh", bit(self.d, 1))

    @extra_op(0x4B)
    def bit_1_e(self):
        self.set_flags("znh", bit(self.e, 1))

    @extra_op(0x4C)
    def bit_1_h(self):
        self.set_flags("znh", bit(self.h, 1))

    @extra_op(0x4D)
    def bit_1_l(self):
        self.set_flags("znh", bit(self.l, 1))

    @extra_op(0x4E)
    def bit_1_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 1))

    @extra_op(0x4F)
    def bit_1_a(self):
        self.set_flags("znh", bit(self.a, 1))

    @extra_op(0x50)
    def bit_2_b(self):
        self.set_flags("znh", bit(self.b, 2))

    @extra_op(0x51)
    def bit_2_c(self):
        self.set_flags("znh", bit(self.c, 2))

    @extra_op(0x52)
    def bit_2_d(self):
        self.set_flags("znh", bit(self.d, 2))

    @extra_op(0x53)
    def bit_2_e(self):
        self.set_flags("znh", bit(self.e, 2))

    @extra_op(0x54)
    def bit_2_h(self):
        self.set_flags("znh", bit(self.h, 2))

    @extra_op(0x55)
    def bit_2_l(self):
        self.set_flags("znh", bit(self.l, 2))

    @extra_op(0x56)
    def bit_2_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 2))

    @extra_op(0x57)
    def bit_2_a(self):
        self.set_flags("znh", bit(self.a, 2))

    @extra_op(0x58)
    def bit_3_b(self):
        self.set_flags("znh", bit(self.b, 3))

    @extra_op(0x59)
    def bit_3_c(self):
        self.set_flags("znh", bit(self.c, 3))

    @extra_op(0x5A)
    def bit_3_d(self):
        self.set_flags("znh", bit(self.d, 3))

    @extra_op(0x5B)
    def bit_3_e(self):
        self.set_flags("znh", bit(self.e, 3))

    @extra_op(0x5C)
    def bit_3_h(self):
        self.set_flags("znh", bit(self.h, 3))

    @extra_op(0x5D)
    def bit_3_l(self):
        self.set_flags("znh", bit(self.l, 3))

    @extra_op(0x5E)
    def bit_3_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 3))

    @extra_op(0x5F)
    def bit_3_a(self):
        self.set_flags("znh", bit(self.a, 3))

    @extra_op(0x60)
    def bit_4_b(self):
        self.set_flags("znh", bit(self.b, 4))

    @extra_op(0x61)
    def bit_4_c(self):
        self.set_flags("znh", bit(self.c, 4))

    @extra_op(0x64)
    def bit_4_d(self):
        self.set_flags("znh", bit(self.d, 4))

    @extra_op(0x63)
    def bit_4_e(self):
        self.set_flags("znh", bit(self.e, 4))

    @extra_op(0x64)
    def bit_4_h(self):
        self.set_flags("znh", bit(self.h, 4))

    @extra_op(0x65)
    def bit_4_l(self):
        self.set_flags("znh", bit(self.l, 4))

    @extra_op(0x66)
    def bit_4_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 4))

    @extra_op(0x67)
    def bit_4_a(self):
        self.set_flags("znh", bit(self.a, 4))

    @extra_op(0x68)
    def bit_5_b(self):
        self.set_flags("znh", bit(self.b, 5))

    @extra_op(0x69)
    def bit_5_c(self):
        self.set_flags("znh", bit(self.c, 5))

    @extra_op(0x6A)
    def bit_5_d(self):
        self.set_flags("znh", bit(self.d, 5))

    @extra_op(0x6B)
    def bit_5_e(self):
        self.set_flags("znh", bit(self.e, 5))

    @extra_op(0x6C)
    def bit_5_h(self):
        self.set_flags("znh", bit(self.h, 5))

    @extra_op(0x6D)
    def bit_5_l(self):
        self.set_flags("znh", bit(self.l, 5))

    @extra_op(0x6E)
    def bit_5_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 5))

    @extra_op(0x6F)
    def bit_5_a(self):
        self.set_flags("znh", bit(self.a, 5))

    @extra_op(0x70)
    def bit_6_b(self):
        self.set_flags("znh", bit(self.b, 6))

    @extra_op(0x71)
    def bit_6_c(self):
        self.set_flags("znh", bit(self.c, 6))

    @extra_op(0x76)
    def bit_6_d(self):
        self.set_flags("znh", bit(self.d, 6))

    @extra_op(0x73)
    def bit_6_e(self):
        self.set_flags("znh", bit(self.e, 6))

    @extra_op(0x76)
    def bit_6_h(self):
        self.set_flags("znh", bit(self.h, 6))

    @extra_op(0x75)
    def bit_6_l(self):
        self.set_flags("znh", bit(self.l, 6))

    @extra_op(0x76)
    def bit_6_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 6))

    @extra_op(0x77)
    def bit_6_a(self):
        self.set_flags("znh", bit(self.a, 6))

    @extra_op(0x78)
    def bit_7_b(self):
        self.set_flags("znh", bit(self.b, 7))

    @extra_op(0x79)
    def bit_7_c(self):
        self.set_flags("znh", bit(self.c, 7))

    @extra_op(0x7A)
    def bit_7_d(self):
        self.set_flags("znh", bit(self.d, 7))

    @extra_op(0x7B)
    def bit_7_e(self):
        self.set_flags("znh", bit(self.e, 7))

    @extra_op(0x7C)
    def bit_7_h(self):
        self.set_flags("znh", bit(self.h, 7))

    @extra_op(0x7D)
    def bit_7_l(self):
        self.set_flags("znh", bit(self.l, 7))

    @extra_op(0x7E)
    def bit_7_addr_hl(self):
        self.set_flags("znh", bit(self._mem.read_byte(self.hl), 7))

    @extra_op(0x7F)
    def bit_7_a(self):
        self.set_flags("znh", bit(self.a, 7))

    @extra_op(0x80)
    def res_0_b(self):
        self.b = reset_bit(self.b, 0).result

    @extra_op(0x81)
    def res_0_c(self):
        self.c = reset_bit(self.c, 0).result

    @extra_op(0x82)
    def res_0_d(self):
        self.d = reset_bit(self.d, 0).result

    @extra_op(0x83)
    def res_0_e(self):
        self.e = reset_bit(self.e, 0).result

    @extra_op(0x84)
    def res_0_h(self):
        self.h = reset_bit(self.h, 0).result

    @extra_op(0x85)
    def res_0_l(self):
        self.l = reset_bit(self.l, 0).result

    @extra_op(0x86)
    def res_0_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 0)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x87)
    def res_0_a(self):
        self.a = reset_bit(self.a, 0).result

    @extra_op(0x88)
    def res_1_b(self):
        self.b = reset_bit(self.b, 1).result

    @extra_op(0x89)
    def res_1_c(self):
        self.c = reset_bit(self.c, 1).result

    @extra_op(0x8A)
    def res_1_d(self):
        self.d = reset_bit(self.d, 1).result

    @extra_op(0x8B)
    def res_1_e(self):
        self.e = reset_bit(self.e, 1).result

    @extra_op(0x8C)
    def res_1_h(self):
        self.h = reset_bit(self.h, 1).result

    @extra_op(0x8D)
    def res_1_l(self):
        self.l = reset_bit(self.l, 1).result

    @extra_op(0x8E)
    def res_1_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 1)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x8F)
    def res_1_a(self):
        self.a = reset_bit(self.a, 1).result

    @extra_op(0x90)
    def res_2_b(self):
        self.b = reset_bit(self.b, 2).result

    @extra_op(0x91)
    def res_2_c(self):
        self.c = reset_bit(self.c, 2).result

    @extra_op(0x92)
    def res_2_d(self):
        self.d = reset_bit(self.d, 2).result

    @extra_op(0x93)
    def res_2_e(self):
        self.e = reset_bit(self.e, 2).result

    @extra_op(0x94)
    def res_2_h(self):
        self.h = reset_bit(self.h, 2).result

    @extra_op(0x95)
    def res_2_l(self):
        self.l = reset_bit(self.l, 2).result

    @extra_op(0x96)
    def res_2_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 2)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x97)
    def res_2_a(self):
        self.a = reset_bit(self.a, 2).result

    @extra_op(0x98)
    def res_3_b(self):
        self.b = reset_bit(self.b, 3).result

    @extra_op(0x99)
    def res_3_c(self):
        self.c = reset_bit(self.c, 3).result

    @extra_op(0x9A)
    def res_3_d(self):
        self.d = reset_bit(self.d, 3).result

    @extra_op(0x9B)
    def res_3_e(self):
        self.e = reset_bit(self.e, 3).result

    @extra_op(0x9C)
    def res_3_h(self):
        self.h = reset_bit(self.h, 3).result

    @extra_op(0x9D)
    def res_3_l(self):
        self.l = reset_bit(self.l, 3).result

    @extra_op(0x9E)
    def res_3_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 3)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0x9F)
    def res_3_a(self):
        self.a = reset_bit(self.a, 3).result

    @extra_op(0xA0)
    def res_4_b(self):
        self.b = reset_bit(self.b, 4).result

    @extra_op(0xA1)
    def res_4_c(self):
        self.c = reset_bit(self.c, 4).result

    @extra_op(0xA2)
    def res_4_d(self):
        self.d = reset_bit(self.d, 4).result

    @extra_op(0xA3)
    def res_4_e(self):
        self.e = reset_bit(self.e, 4).result

    @extra_op(0xA4)
    def res_4_h(self):
        self.h = reset_bit(self.h, 4).result

    @extra_op(0xA5)
    def res_4_l(self):
        self.l = reset_bit(self.l, 4).result

    @extra_op(0xA6)
    def res_4_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 4)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xA7)
    def res_4_a(self):
        self.a = reset_bit(self.a, 4).result

    @extra_op(0xA8)
    def res_5_b(self):
        self.b = reset_bit(self.b, 5).result

    @extra_op(0xA9)
    def res_5_c(self):
        self.c = reset_bit(self.c, 5).result

    @extra_op(0xAA)
    def res_5_d(self):
        self.d = reset_bit(self.d, 5).result

    @extra_op(0xAB)
    def res_5_e(self):
        self.e = reset_bit(self.e, 5).result

    @extra_op(0xAC)
    def res_5_h(self):
        self.h = reset_bit(self.h, 5).result

    @extra_op(0xAD)
    def res_5_l(self):
        self.l = reset_bit(self.l, 5).result

    @extra_op(0xAE)
    def res_5_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 5)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xAF)
    def res_5_a(self):
        self.a = reset_bit(self.a, 5).result

    @extra_op(0xB0)
    def res_6_b(self):
        self.b = reset_bit(self.b, 6).result

    @extra_op(0xB1)
    def res_6_c(self):
        self.c = reset_bit(self.c, 6).result

    @extra_op(0xB2)
    def res_6_d(self):
        self.d = reset_bit(self.d, 6).result

    @extra_op(0xB3)
    def res_6_e(self):
        self.e = reset_bit(self.e, 6).result

    @extra_op(0xB4)
    def res_6_h(self):
        self.h = reset_bit(self.h, 6).result

    @extra_op(0xB5)
    def res_6_l(self):
        self.l = reset_bit(self.l, 6).result

    @extra_op(0xB6)
    def res_6_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 6)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xB7)
    def res_6_a(self):
        self.a = reset_bit(self.a, 6).result

    @extra_op(0xB8)
    def res_7_b(self):
        self.b = reset_bit(self.b, 7).result

    @extra_op(0xB9)
    def res_7_c(self):
        self.c = reset_bit(self.c, 7).result

    @extra_op(0xBA)
    def res_7_d(self):
        self.d = reset_bit(self.d, 7).result

    @extra_op(0xBB)
    def res_7_e(self):
        self.e = reset_bit(self.e, 7).result

    @extra_op(0xBC)
    def res_7_h(self):
        self.h = reset_bit(self.h, 7).result

    @extra_op(0xBD)
    def res_7_l(self):
        self.l = reset_bit(self.l, 7).result

    @extra_op(0xBE)
    def res_7_addr_hl(self):
        res = reset_bit(self._mem.read_byte(self.hl), 7)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xBF)
    def res_7_a(self):
        self.a = reset_bit(self.a, 7).result

    @extra_op(0xC0)
    def set_0_b(self):
        self.b = set_bit(self.b, 0).result

    @extra_op(0xC1)
    def set_0_c(self):
        self.c = set_bit(self.c, 0).result

    @extra_op(0xC2)
    def set_0_d(self):
        self.d = set_bit(self.d, 0).result

    @extra_op(0xC3)
    def set_0_e(self):
        self.e = set_bit(self.e, 0).result

    @extra_op(0xC4)
    def set_0_h(self):
        self.h = set_bit(self.h, 0).result

    @extra_op(0xC5)
    def set_0_l(self):
        self.l = set_bit(self.l, 0).result

    @extra_op(0xC6)
    def set_0_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 0)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xC7)
    def set_0_a(self):
        self.a = set_bit(self.a, 0).result

    @extra_op(0xC8)
    def set_1_b(self):
        self.b = set_bit(self.b, 1).result

    @extra_op(0xC9)
    def set_1_c(self):
        self.c = set_bit(self.c, 1).result

    @extra_op(0xCA)
    def set_1_d(self):
        self.d = set_bit(self.d, 1).result

    @extra_op(0xCB)
    def set_1_e(self):
        self.e = set_bit(self.e, 1).result

    @extra_op(0xCC)
    def set_1_h(self):
        self.h = set_bit(self.h, 1).result

    @extra_op(0xCD)
    def set_1_l(self):
        self.l = set_bit(self.l, 1).result

    @extra_op(0xCE)
    def set_1_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 1)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xCF)
    def set_1_a(self):
        self.a = set_bit(self.a, 1).result

    @extra_op(0xD0)
    def set_2_b(self):
        self.b = set_bit(self.b, 2).result

    @extra_op(0xD1)
    def set_2_c(self):
        self.c = set_bit(self.c, 2).result

    @extra_op(0xD2)
    def set_2_d(self):
        self.d = set_bit(self.d, 2).result

    @extra_op(0xD3)
    def set_2_e(self):
        self.e = set_bit(self.e, 2).result

    @extra_op(0xD4)
    def set_2_h(self):
        self.h = set_bit(self.h, 2).result

    @extra_op(0xD5)
    def set_2_l(self):
        self.l = set_bit(self.l, 2).result

    @extra_op(0xD6)
    def set_2_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 2)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xD7)
    def set_2_a(self):
        self.a = set_bit(self.a, 2).result

    @extra_op(0xD8)
    def set_3_b(self):
        self.b = set_bit(self.b, 3).result

    @extra_op(0xD9)
    def set_3_c(self):
        self.c = set_bit(self.c, 3).result

    @extra_op(0xDA)
    def set_3_d(self):
        self.d = set_bit(self.d, 3).result

    @extra_op(0xDB)
    def set_3_e(self):
        self.e = set_bit(self.e, 3).result

    @extra_op(0xDC)
    def set_3_h(self):
        self.h = set_bit(self.h, 3).result

    @extra_op(0xDD)
    def set_3_l(self):
        self.l = set_bit(self.l, 3).result

    @extra_op(0xDE)
    def set_3_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 3)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xDF)
    def set_3_a(self):
        self.a = set_bit(self.a, 3).result

    @extra_op(0xE0)
    def set_4_b(self):
        self.b = set_bit(self.b, 4).result

    @extra_op(0xE1)
    def set_4_c(self):
        self.c = set_bit(self.c, 4).result

    @extra_op(0xE2)
    def set_4_d(self):
        self.d = set_bit(self.d, 4).result

    @extra_op(0xE3)
    def set_4_e(self):
        self.e = set_bit(self.e, 4).result

    @extra_op(0xE4)
    def set_4_h(self):
        self.h = set_bit(self.h, 4).result

    @extra_op(0xE5)
    def set_4_l(self):
        self.l = set_bit(self.l, 4).result

    @extra_op(0xE6)
    def set_4_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 4)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xE7)
    def set_4_a(self):
        self.a = set_bit(self.a, 4).result

    @extra_op(0xE8)
    def set_5_b(self):
        self.b = set_bit(self.b, 5).result

    @extra_op(0xE9)
    def set_5_c(self):
        self.c = set_bit(self.c, 5).result

    @extra_op(0xEA)
    def set_5_d(self):
        self.d = set_bit(self.d, 5).result

    @extra_op(0xEB)
    def set_5_e(self):
        self.e = set_bit(self.e, 5).result

    @extra_op(0xEC)
    def set_5_h(self):
        self.h = set_bit(self.h, 5).result

    @extra_op(0xED)
    def set_5_l(self):
        self.l = set_bit(self.l, 5).result

    @extra_op(0xEE)
    def set_5_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 5)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xEF)
    def set_5_a(self):
        self.a = set_bit(self.a, 5).result

    @extra_op(0xF0)
    def set_6_b(self):
        self.b = set_bit(self.b, 6).result

    @extra_op(0xF1)
    def set_6_c(self):
        self.c = set_bit(self.c, 6).result

    @extra_op(0xF2)
    def set_6_d(self):
        self.d = set_bit(self.d, 6).result

    @extra_op(0xF3)
    def set_6_e(self):
        self.e = set_bit(self.e, 6).result

    @extra_op(0xF4)
    def set_6_h(self):
        self.h = set_bit(self.h, 6).result

    @extra_op(0xF5)
    def set_6_l(self):
        self.l = set_bit(self.l, 6).result

    @extra_op(0xF6)
    def set_6_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 6)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xF7)
    def set_6_a(self):
        self.a = set_bit(self.a, 6).result

    @extra_op(0xF8)
    def set_7_b(self):
        self.b = set_bit(self.b, 7).result

    @extra_op(0xF9)
    def set_7_c(self):
        self.c = set_bit(self.c, 7).result

    @extra_op(0xFA)
    def set_7_d(self):
        self.d = set_bit(self.d, 7).result

    @extra_op(0xFB)
    def set_7_e(self):
        self.e = set_bit(self.e, 7).result

    @extra_op(0xFC)
    def set_7_h(self):
        self.h = set_bit(self.h, 7).result

    @extra_op(0xFD)
    def set_7_l(self):
        self.l = set_bit(self.l, 7).result

    @extra_op(0xFE)
    def set_7_addr_hl(self):
        res = set_bit(self._mem.read_byte(self.hl), 7)
        self._mem.write_byte(res.result, self.hl)

    @extra_op(0xFF)
    def set_7_a(self):
        self.a = set_bit(self.a, 7).result


ALUResult = namedtuple("ALUResult",
                       ["result", "z_flag", "n_flag", "h_flag", "c_flag"])


def add_8bit(a, b, c=0):
    n_flag = False
    c_flag = (a + b + c) & 0x1FF > 0xFF
    h_flag = ((a & 0xF) + (b & 0xF)) + c > 0xF
    val = (a + b + c) & 0xFF
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def sub_8bit(a, b, c=0):
    n_flag = True
    res = add_8bit(a, -(b + c))
    return ALUResult(res.result, res.z_flag, n_flag, res.h_flag, res.c_flag)


def add_16bit(a, b):
    n_flag = False
    c_flag = (a + b) & 0x1FFFF > 0xFFFF
    h_flag = ((a & 0xFFF) + (b & 0xFFF)) > 0xFFF
    val = (a + b) & 0xFFFF
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def sub_16bit(a, b):
    n_flag = True
    res = add_16bit(a, -b)
    return ALUResult(res.result, res.z_flag, n_flag, res.h_flag, res.c_flag)


def rotate_right(a):
    val = a >> 1
    val |= (a & 1) << 7
    c_flag = bool(a & 1)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def rotate_right_through_carry(a, c=0):
    val = a >> 1
    val |= c << 7
    c_flag = bool(a & 1)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def rotate_left(a):
    val = (a << 1) & 0xFF
    val |= (a >> 7)
    c_flag = bool(a & 0x80)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def rotate_left_through_carry(a, c=0):
    val = (a << 1) & 0xFF
    val |= c
    c_flag = bool(a & 0x80)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def signed_8bit(a):
    if a & 0x80:
        return (-1 & ~ 0xFF) | a
    return a


def shift_left(a):
    val = (a << 1) & 0xFF
    c_flag = bool(a & 0x80)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def shift_right_arithmetic(a):
    val = (a >> 1) & 0xFF
    if a & 0x80:
        val |= 0x80
    c_flag = bool(a & 0x1)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def shift_right_logical(a):
    val = (a >> 1) & 0xFF
    c_flag = bool(a & 0x1)
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def swap(a):
    val = ((a & 0xF0) >> 4) | ((a & 0xF) << 4)
    c_flag = False
    n_flag = False
    h_flag = False
    z_flag = val == 0
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def bit(a, b):
    c_flag = False
    n_flag = False
    h_flag = True
    z_flag = not (a & (1 << b))
    return ALUResult(None, z_flag, n_flag, h_flag, c_flag)


def reset_bit(a, b):
    val = (a & ~(1 << b)) & 0xFF
    c_flag = False
    n_flag = False
    h_flag = False
    z_flag = False
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)


def set_bit(a, b):
    val = (a | (1 << b)) & 0xFF
    c_flag = False
    n_flag = False
    h_flag = False
    z_flag = False
    return ALUResult(val, z_flag, n_flag, h_flag, c_flag)
