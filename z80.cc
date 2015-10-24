#include <cstdint>

uint8_t Z_FLAG = 1 << 7;
uint8_t N_FLAG = 1 << 6;
uint8_t H_FLAG = 1 << 5;
uint8_t C_FLAG = 1 << 4;

using reg_16_8_map =
    union {
        uint16_t reg16;
        struct {
            uint8_t hi;
            uint8_t low;
        } reg8;
    };

class Z80 {
    reg_16_8_map af, bc, de, hl;
    uint16_t pc;
    uint8_t add_8bit(uint8_t& a, uint8_t b, uint8_t c);
    uint8_t sub_8bit(uint8_t& a, uint8_t b, uint8_t c);
public:
    Z80() : pc(0) { af.reg16=0; bc.reg16=0, de.reg16=0; hl.reg16=0; }
};

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
