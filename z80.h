#include <cstdint>
#ifndef Z80_H
#define Z80_H

struct Z80 {
    union {
        uint16_t reg_af;
        struct {
            union {
                uint8_t reg_f;
                struct {
                    uint8_t :4;
                    uint8_t z_flag :1;
                    uint8_t n_flag :1;
                    uint8_t h_flag :1;
                    uint8_t c_flag :1;
                };
            };
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
    Z80() : reg_af(0), reg_bc(0), reg_de(0), reg_hl(0), pc(0) {}

    void adc_8bit(uint8_t &, uint8_t, uint8_t);
    uint8_t add_a_b();
    uint8_t add_a_c();
    uint8_t add_a_d();
    uint8_t add_a_e();
    uint8_t add_a_h();
    uint8_t add_a_l();
    uint8_t add_a_a();
    uint8_t adc_a_b();
    uint8_t adc_a_c();
    uint8_t adc_a_d();
    uint8_t adc_a_e();
    uint8_t adc_a_h();
    uint8_t adc_a_l();
    uint8_t adc_a_a();
};

#endif
