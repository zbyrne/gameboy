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
    def set(self, val):
        self.b = (val >> 8) & 0xFF
        self.c = val & 0xFF

    @property
    def de(self):
        return (self.d << 8) + self.e

    @de.setter
    def set(self, val):
        self.d = (val >> 8) & 0xFF
        self.e = val & 0xFF

    @property
    def hl(self):
        return (self.h << 8) + self.l

    @hl.setter
    def set(self, val):
        self.h = (val >> 8) & 0xFF
        self.l = val & 0xFF

    @property
    def z_flag(self):
        return bool(self.f & Z_FLAG)

    @z_flag.setter
    def set(self, val):
        if val:
            self.f |= Z_FLAG
        else:
            self.f &= ~Z_FLAG

    @property
    def n_flag(self):
        return bool(self.f & N_FLAG)

    @n_flag.setter
    def set(self, val):
        if val:
            self.f |= N_FLAG
        else:
            self.f &= ~N_FLAG

    @property
    def h_flag(self):
        return bool(self.f & H_FLAG)

    @h_flag.setter
    def set(self, val):
        if val:
            self.f |= H_FLAG
        else:
            self.f &= ~H_FLAG

    @property
    def c_flag(self):
        return bool(self.f & C_FLAG)

    @c_flag.setter
    def set(self, val):
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
        self.bc += 1
        self.pc += 1
        return 8

    def inc_b(self):
        self.h_flag = ((self.b & 0xF) + 1) > 0xF
        self.b = (self.b + 1) & 0xFF
        self.z_flag = self.b == 0
        self.n_flag = False
        self.pc += 1
        return 4

    def dec_b(self):
        self.h_flag = (self.b & 0xF0) > ((self.b - 1) & 0xF0)
        self.b = 0xFF if self.b == 0 else (self.b - 1) & 0xFF
        self.z_flag = self.b == 0
        self.n_flag = True
        self.pc += 1
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
        self.n_flag = False
        self.c_flag = (self.hl + self.bc) > 0xFFFF
        self.h_flag = ((self.hl & 0xFFF) + (self.bc & 0xFFF)) > 0xFFF
        self.hl = (self.hl + self.pc) & 0xFFFF
        return 8
