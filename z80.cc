#include <cstdint>
#include "z80.h"

uint8_t
Z80::add_a_b() {
    uint8_t result = this->reg_a + this->reg_b;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_b & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_b) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::add_a_c() {
    uint8_t result = this->reg_a + this->reg_c;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_c & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_c) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::add_a_d() {
    uint8_t result = this->reg_a + this->reg_d;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_d & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_d) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::add_a_e() {
    uint8_t result = this->reg_a + this->reg_e;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_e & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_e) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::add_a_h() {
    uint8_t result = this->reg_a + this->reg_h;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_h & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_h) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::add_a_l() {
    uint8_t result = this->reg_a + this->reg_l;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_l & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_l) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::add_a_a() {
    uint8_t result = this->reg_a + this->reg_a;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_a & 0xF) > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - this->reg_a) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_b() {
    uint8_t result = this->reg_a + this->reg_b + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_b & 0xF) + this->c_flag > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_b + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_c() {
    uint8_t result = this->reg_a + this->reg_c + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_c & 0xF) + this->c_flag > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_c + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_d() {
    uint8_t result = this->reg_a + this->reg_d + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_d & 0xF) + this->c_flag > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_d + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_e() {
    uint8_t result = this->reg_a + this->reg_e + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_e & 0xF) > 0xF) ? 1 : 0 + this->c_flag;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_e + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_h() {
    uint8_t result = this->reg_a + this->reg_h + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_h & 0xF) + this->c_flag > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_h + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_l() {
    uint8_t result = this->reg_a + this->reg_l + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_l & 0xF) + this->c_flag> 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_l + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}

uint8_t
Z80::adc_a_a() {
    uint8_t result = this->reg_a + this->reg_a + this->c_flag;
    this->z_flag = (result == 0) ? 1 : 0;
    this->n_flag = 0;
    this->h_flag = ((this->reg_a & 0xF) + (this->reg_a & 0xF) + this->c_flag > 0xF) ? 1 : 0;
    this->c_flag = (this->reg_a > UINT8_MAX - (this->reg_a + this->c_flag)) ? 1 : 0;
    this->reg_a = result;
    this->pc++;
    return 4;
}
