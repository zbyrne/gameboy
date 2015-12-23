#include <cstdint>
#ifndef Z80_H
#define Z80_H

enum class Flags {
    CLEAR = 0,
    C_FLAG = 1 << 4,
    H_FLAG = 1 << 5,
    N_FLAG = 1 << 6,
    Z_FLAG = 1 << 7
};

class Z80 {
    union {
        uint16_t reg_af;
        struct {
            uint8_t reg_f;
            uint8_t reg_a;
        };
    };
    union {
        uint16_t reg_bc;
        struct {
            uint8_t reg_c;
            uint8_t reg_b;
        };
    };
    union {
        uint16_t reg_de;
        struct {
            uint8_t reg_e;
            uint8_t reg_d;
        };
    };
    union {
        uint16_t reg_hl;
        struct {
            uint8_t reg_l;
            uint8_t reg_h;
        };
    };
    uint16_t pc;
    uint8_t add_8bit(uint8_t& a, uint8_t b, uint8_t c);
    uint8_t sub_8bit(uint8_t& a, uint8_t b, uint8_t c);
public:
    Z80() : reg_af(0), reg_bc(0), reg_de(0), reg_hl(0), pc(0) {}
};

#endif
