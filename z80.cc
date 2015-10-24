#include <cstdint>

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
public:
    Z80() : pc(0) { af.reg16=0; bc.reg16=0, de.reg16=0; hl.reg16=0; }
};
