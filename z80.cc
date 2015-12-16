#include <cstdint>
#include "z80.h"

constexpr uint8_t Z_FLAG = 1 << 7;
constexpr uint8_t N_FLAG = 1 << 6;
constexpr uint8_t H_FLAG = 1 << 5;
constexpr uint8_t C_FLAG = 1 << 4;

uint8_t
Z80::add_8bit(uint8_t& a, uint8_t b, uint8_t c) {
    uint8_t result = a + b + c;
    uint8_t flags = 0;
    flags |= (result == 0) ? Z_FLAG : 0;
    flags |= ((a & 0xF) + (b & 0xF) + c > 0xF) ? H_FLAG : 0;
    flags |= (a > UINT8_MAX - (b + c)) ? C_FLAG : 0;
    a = result;
    return flags;
}
