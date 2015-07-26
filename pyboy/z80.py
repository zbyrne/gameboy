from collections import namedtuple


Z_FLAG = 1 << 7
N_FLAG = 1 << 6
H_FLAG = 1 << 5
C_FLAG = 1 << 4


class Z80(object):

    def __init__(self, mem):
        self._mem = mem
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0
        self.sp = 0
        self.pc = 0

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

    def nop(self):
        self.pc += 1
        return 4

    def ld_bc_d16(self):
        self.pc += 1
        self.bc = self._mem.read_word(self.pc)
        self.pc += 2
        return 12

    def ld_addr_bc_a(self):
        self._mem.write_byte(self.a, self.bc)
        self.pc +=1
        return 8

    def inc_bc(self):
        self.pc += 1
        self.bc = add_16bit(self.bc, 1).result
        return 8

    def inc_b(self):
        self.pc += 1
        res = add_8bit(self.b, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.b = res.result
        return 4

    def dec_b(self):
        self.pc += 1
        res = sub_8bit(self.b, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.b = res.result
        return 4

    def ld_b_d8(self):
        self.pc += 1
        self.b = self._mem.read_byte(self.pc)
        self.pc += 1
        return 8

    def rlca(self):
        self.pc +=1
        self.f = 0
        self.c_flag = bool(self.a & (1<<7))
        self.a <<= 1
        self.a &= 0xFF
        self.a += int(self.c_flag)
        return 4

    def ld_a16_sp(self):
        self.pc +=1
        addr = self._mem.read_word(self.pc)
        self.pc += 2
        self._mem.write_word(self.sp, addr)
        return 20

    def add_hl_bc(self):
        self.pc += 1
        res = add_16bit(self.hl, self.bc)
        self.n_flag = res.n_flag
        self.c_flag = res.c_flag
        self.h_flag = res.h_flag
        self.hl = res.result
        return 8

    def ld_a_addr_bc(Self):
        self.pc += 1
        self.a = self._mem.read_byte(self.bc)
        return 8

    def dec_bc(self):
        self.pc += 1
        self.bc = sub_16bit(self.bc, 1).result
        return 8

    def inc_c(self):
        self.pc += 1
        res = add_8bit(self.c, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.c = res.result
        return 4

    def dec_c(self):
        self.pc += 1
        res = sub_8bit(self.c, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.c = res.result
        return 4

    def ld_c_d8(self):
        self.pc += 1
        self.c = self._mem.read_byte(self.pc)
        self.pc += 1
        return 8

    def rrca(self):
        self.pc +=1
        self.f = 0
        self.c_flag = bool(self.a & 1)
        self.a >>= 1
        self.a &= 0xFF
        self.a |= int(self.c_flag) << 7
        self.z_flag = self.a == 0
        return 4

    def stop(self):
        """
        Going to have to do something silly here to stop the cpu.
        """
        self.pc += 2
        return 4

    def ld_de_d16(self):
        self.pc += 1
        self.de = self._mem.read_word(self.pc)
        self.pc += 2
        return 12

    def ld_addr_de_a(self):
        self._mem.write_byte(self.a, self.de)
        self.pc +=1
        return 8

    def inc_de(self):
        self.pc += 1
        self.de = add_16bit(self.de, 1).result
        return 8

    def inc_d(self):
        self.pc += 1
        res = add_8bit(self.d, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.d = res.result
        return 4

    def dec_d(self):
        self.pc += 1
        res = sub_8bit(self.d, 1)
        self.h_flag = res.h_flag
        self.z_flag = res.z_flag
        self.n_flag = res.n_flag
        self.d = res.result
        return 4

    def ld_d_d8(self):
        self.pc += 1
        self.d = self._mem.read_byte(self.pc)
        self.pc += 1
        return 8


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