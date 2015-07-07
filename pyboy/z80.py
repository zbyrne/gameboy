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
