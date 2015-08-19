class MemoryController(object):
    def __init__(self, cart_path):
        with open(cart_path, 'rb+') as cart:
            rom = cart.read()
        rom_bank = [ord(x) for x in rom]
        ram_bank = [0]*0x8000
        self.memory = rom_bank + ram_bank

    def read_byte(self, addr):
        return self.memory[addr]

    def write_byte(self, val, addr):
        self.memory[addr] = val

    def read_word(self, addr):
        l = self.memory[addr]
        h = self.memory[addr + 1]
        return (h << 8) + l

    def write_word(self, val, addr):
        self.memory[addr] = val & 0xFF
        self.memory[addr + 1] = (val >> 8) & 0xFF
