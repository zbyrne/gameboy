class Z80(object):

    def __init__(self):
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
