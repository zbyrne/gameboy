#include <iostream>
#include "z80.h"

int main() {
    auto z = Z80();
    z.z_flag = 1;
    std::cout << z.reg_af << std::endl;
    return 0;
}
