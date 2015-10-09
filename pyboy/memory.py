from collections import namedtuple


MappedController = namedtuple('MappedController',
                              ('controller', 'start', 'length'))


class MemoryController(object):
    def __init__(self):
        self._memory_map = []

    def register_controller(self, controller, start):
        con = MappedController(controller, start, len(controller))
        self._memory_map.append(con)

    def _get_controller(self, addr):
        for con in self._memory_map:
            if addr >= con.start:
                if addr - con.start < con.length:
                    return con
        raise IndexError("memory out of range: 0x%x" % addr)

    def read_byte(self, addr):
        con = self._get_controller(addr)
        return con.controller[addr - con.start]

    def write_byte(self, val, addr):
        con = self._get_controller(addr)
        con.controller[addr - con.start] = val

    def read_word(self, addr):
        con = self._get_controller(addr)
        l = con.controller[addr - con.start]
        h = con.controller[addr - con.start + 1]
        return (h << 8) + l

    def write_word(self, val, addr):
        con = self._get_controller(addr)
        con.controller[addr - con.start] = val & 0xFF
        con.controller[addr - con.start + 1] = (val >> 8) & 0xFF


class RamController(list):
    def __init__(self, size):
        self.extend([0]*size)
