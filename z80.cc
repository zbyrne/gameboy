#include <cstdint>
#include "z80.h"

uint8_t
Z80::add_8bit(uint8_t& a, uint8_t b, uint8_t c) {
    uint8_t result = a + b + c;
    uint8_t flags = 0;
    flags |= (result == 0) ? static_cast<uint8_t>(Flags::Z_FLAG) : 0;
    flags |= ((a & 0xF) + (b & 0xF) + c > 0xF) ? static_cast<uint8_t>(Flags::H_FLAG) : 0;
    flags |= (a > UINT8_MAX - (b + c)) ? static_cast<uint8_t>(Flags::C_FLAG) : 0;
    a = result;
    return flags;
}

uint8_t
Z80::sub_8bit(uint8_t& a, uint8_t b, uint8_t c) {
    return this->add_8bit(a, -b, c);
}
