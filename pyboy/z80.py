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
        for attr in dir(self):
            attr = getattr(self, attr)
            if hasattr(attr, "op_code"):
                self.op_map[attr.op_code] = attr
        self.extra_ops_map = {}

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
    # Return clock cycles used.
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
        offset = signed_8bit(self._mem.read_byte(self.pc + 1))
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
        offset = signed_8bit(self._mem.read_byte(self.pc + 1))
        if not self.z_flag:
            self.pc += offset
            return True
        self.pc += 2

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
        offset = signed_8bit(self._mem.read_byte(self.pc + 1))
        if self.z_flag:
            self.pc += offset
            return True
        self.pc += 2

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
        offset = signed_8bit(self._mem.read_byte(self.pc + 1))
        if not self.c_flag:
            self.pc += offset
            return True
        self.pc += 2

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
        offset = signed_8bit(self._mem.read_byte(self.pc + 1))
        if self.c_flag:
            self.pc += offset
            return True
        self.pc += 2

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
    def pop_bc(self):
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

    @op_code(0xCE, 4)
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
        return -(0xFF - a)
    return a
