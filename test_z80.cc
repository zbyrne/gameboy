#include <iostream>
#include "z80.h"

int main() {
    auto z = Z80();
    z.reg_b = 4;
    z.add_a_b();
    std::cout << static_cast<uint32_t>(z.reg_a) << std::endl;
    return 0;
}
