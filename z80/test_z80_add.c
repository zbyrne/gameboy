#include <stdint.h>
#include <string.h>
#include "z80.h"
#include "testme.h"

uint8_t mem_read(uint16_t addr){return 0;}
void mem_write(uint16_t addr, uint8_t val){}

TESTME_START(test_z80_add_hl_16bit)
{
    Z80_t proc;
    proc.registers.b = 0x1;
    proc.registers.c = 0x2;
    proc.registers.h = 0x3;
    proc.registers.l = 0x4;
    proc.registers.f = 0;
    Z80Clocks_t clocks = ADD_HL_16bit(&proc, &proc.registers.b,
                                      &proc.registers.c);
    TESTME_ASSERT_INT_EQ(clocks.m, 2);
    TESTME_ASSERT_INT_EQ(clocks.t, 8);
    TESTME_ASSERT_INT_EQ(proc.registers.h, 0x4);
    TESTME_ASSERT_INT_EQ(proc.registers.l, 0x6);
    TESTME_ASSERT_INT_EQ(proc.registers.f, 0);
}
TESTME_END

TESTME_START(test_z80_add_hl_16bit_half_carry)
{
    Z80_t proc;
    proc.registers.b = 0xF;
    proc.registers.c = 0x0;
    proc.registers.h = 0x1;
    proc.registers.l = 0x0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = ADD_HL_16bit(&proc, &proc.registers.b,
                                      &proc.registers.c);
    TESTME_ASSERT_INT_EQ(clocks.m, 2);
    TESTME_ASSERT_INT_EQ(clocks.t, 8);
    TESTME_ASSERT_INT_EQ(proc.registers.h, 0x10);
    TESTME_ASSERT_INT_EQ(proc.registers.l, 0x0);
    TESTME_ASSERT_INT_EQ(proc.registers.f, Z80_HALF_CARRY);
}
TESTME_END

TESTME_START(test_z80_add_hl_16bit_carry)
{
    Z80_t proc;
    proc.registers.b = 0xF0;
    proc.registers.c = 0x0;
    proc.registers.h = 0x10;
    proc.registers.l = 0x0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = ADD_HL_16bit(&proc, &proc.registers.b,
                                      &proc.registers.c);
    TESTME_ASSERT_INT_EQ(clocks.m, 2);
    TESTME_ASSERT_INT_EQ(clocks.t, 8);
    TESTME_ASSERT_INT_EQ(proc.registers.h, 0x0);
    TESTME_ASSERT_INT_EQ(proc.registers.l, 0x0);
    TESTME_ASSERT_INT_EQ(proc.registers.f, Z80_CARRY);
}
TESTME_END

TESTME_SUITE(test_z80_add)
{
    TESTME_SUITE_RUN_TEST(test_z80_add_hl_16bit);
    TESTME_SUITE_RUN_TEST(test_z80_add_hl_16bit_half_carry);
    TESTME_SUITE_RUN_TEST(test_z80_add_hl_16bit_carry);
}
TESTME_SUITE_END
