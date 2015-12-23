#include <cstdint>
#include "z80.h"

uint8_t
operator|(const uint8_t &a, const Flags &b) {
    return a | static_cast<uint8_t>(b);
}

uint8_t
operator|=(const uint8_t &a, const Flags &b) {
    return a | static_cast<uint8_t>(b);
}

uint8_t
operator~(const Flags &a) {
    return ~static_cast<uint8_t>(a);
}

uint8_t
Z80::add_8bit(uint8_t& a, uint8_t b, uint8_t c) {
    uint8_t result = a + b + c;
    uint8_t flags = 0;
    flags |= (result == 0) ? Flags::Z_FLAG : Flags::CLEAR;
    flags |= ((a & 0xF) + (b & 0xF) + c > 0xF) ? Flags::H_FLAG : Flags::CLEAR;
    flags |= (a > UINT8_MAX - (b + c)) ? Flags::C_FLAG : Flags::CLEAR;
    a = result;
    return flags;
}

uint8_t
Z80::sub_8bit(uint8_t& a, uint8_t b, uint8_t c) {
    return this->add_8bit(a, -b, c) | Flags::N_FLAG;
}
