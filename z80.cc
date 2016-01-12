#include <cstdint>
#include "z80.h"

void
Z80::adc_8bit(uint8_t &dest, uint8_t src, uint8_t carry) {
    uint8_t result = dest + src + carry;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((dest & 0xF) + (src & 0xF) + carry > 0xF) ? 1 : 0;
    this->c_flag = (dest > UINT8_MAX - (src + carry)) ? 1 : 0;
    dest = result;
    this->pc++;
}

uint8_t
Z80::add_a_b() {
    this->adc_8bit(this->reg_a, this->reg_b, 0);
    return 4;
}

uint8_t
Z80::add_a_c() {
    this->adc_8bit(this->reg_a, this->reg_c, 0);
    return 4;
}

uint8_t
Z80::add_a_d() {
    this->adc_8bit(this->reg_a, this->reg_d, 0);
    return 4;
}

uint8_t
Z80::add_a_e() {
    this->adc_8bit(this->reg_a, this->reg_e, 0);
    return 4;
}

uint8_t
Z80::add_a_h() {
    this->adc_8bit(this->reg_a, this->reg_h, 0);
    return 4;
}

uint8_t
Z80::add_a_l() {
    this->adc_8bit(this->reg_a, this->reg_l, 0);
    return 4;
}

uint8_t
Z80::add_a_a() {
    this->adc_8bit(this->reg_a, this->reg_a, 0);
    return 4;
}

uint8_t
Z80::adc_a_b() {
    this->adc_8bit(this->reg_a, this->reg_b, this->c_flag);
    return 4;
}

uint8_t
Z80::adc_a_c() {
    this->adc_8bit(this->reg_a, this->reg_c, this->c_flag);
    return 4;
}

uint8_t
Z80::adc_a_d() {
    this->adc_8bit(this->reg_a, this->reg_d, this->c_flag);
    return 4;
}

uint8_t
Z80::adc_a_e() {
    this->adc_8bit(this->reg_a, this->reg_e, this->c_flag);
    return 4;
}

uint8_t
Z80::adc_a_h() {
    this->adc_8bit(this->reg_a, this->reg_h, this->c_flag);
    return 4;
}

uint8_t
Z80::adc_a_l() {
    this->adc_8bit(this->reg_a, this->reg_l, this->c_flag);
    return 4;
}

uint8_t
Z80::adc_a_a() {
    this->adc_8bit(this->reg_a, this->reg_a, this->c_flag);
    return 4;
}
