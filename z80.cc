#include <cstdint>

constexpr uint8_t Z_FLAG = 1 << 7;
constexpr uint8_t N_FLAG = 1 << 6;
constexpr uint8_t H_FLAG = 1 << 5;
constexpr uint8_t C_FLAG = 1 << 4;

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
