from collections import namedtuple
from functools import wraps


Z_FLAG = 1 << 7
N_FLAG = 1 << 6
H_FLAG = 1 << 5
C_FLAG = 1 << 4


def op_code(code, cycles):
    """
    Decorator for methods of Z80 that implement instructions.  Causes
    the method to return the number of clock cycles consumed.
    """
    def dec(fn):
        setattr(fn, "op_code", code)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn(*args, **kwargs)
            return cycles
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
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.b = res.result

    @op_code(0x5, 4)
    def dec_b(self):
        self.pc += 1
        res = sub_8bit(self.b, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
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
        self.a = res.result
        self.c_flag = res.c_flag
        self.n_flag = res.n_flag
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag

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
        self.n_flag = res.n_flag
        self.c_flag = res.c_flag
        self.h_flag = res.h_flag
        self.hl = res.result

    @op_code(0xA, 8)
    def ld_a_addr_bc(Self):
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
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.c = res.result

    @op_code(0xD, 4)
    def dec_c(self):
        self.pc += 1
        res = sub_8bit(self.c, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
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
        self.a = res.result
        self.c_flag = res.c_flag
        self.n_flag = res.n_flag
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag

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
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.d = res.result

    @op_code(0x15, 4)
    def dec_d(self):
        self.pc += 1
        res = sub_8bit(self.d, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.d = res.result

    @op_code(0x16, 8)
    def ld_d_d8(self):
        self.pc += 1
        self.d = self._mem.read_byte(self.pc)
        self.pc += 1


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
    return ALUResult(res.result, res.z_flag, n_flag, res.h_flag, not res.c_flag)


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
    return ALUResult(res.result, res.z_flag, n_flag, res.h_flag, not res.c_flag)


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
