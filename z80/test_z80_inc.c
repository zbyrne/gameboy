#include <stdint.h>
#include <string.h>
#include "z80.h"
#include "testme.h"

uint8_t mem_read(uint16_t addr){return 0;}
void mem_write(uint16_t addr, uint8_t val){}

TESTME_START(test_z80_inc_16bit)
{
    Z80_t proc;
    proc.registers.b = 1;
    proc.registers.c = 0xFF;
    Z80Clocks_t clocks = INC_16bit(&proc, &proc.registers.b, &proc.registers.c);
    TESTME_ASSERT_INT_EQ(clocks.m, 2);
    TESTME_ASSERT_INT_EQ(clocks.t, 8);
    uint16_t result = (proc.registers.b << 8) + proc.registers.c;
    TESTME_ASSERT_INT_EQ(result, 0x200);
}
TESTME_END

TESTME_START(test_z80_inc_reg_zero)
{
    Z80_t proc;
    proc.registers.b = 0xFF;
    proc.registers.f = 0;
    Z80Clocks_t clocks = INC_reg(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 0);
    /* 0xFF + 1 does indeed half-carry */
    uint8_t flags = Z80_ZERO | Z80_HALF_CARRY;
    TESTME_ASSERT_INT_EQ(proc.registers.f, flags);
}
TESTME_END

TESTME_START(test_z80_inc_reg_not_zero)
{
    Z80_t proc;
    proc.registers.b = 5;
    proc.registers.f = 0;
    Z80Clocks_t clocks = INC_reg(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 6);
    TESTME_ASSERT_INT_EQ(proc.registers.f, 0);
}
TESTME_END

TESTME_START(test_z80_inc_reg_half_carry)
{
    Z80_t proc;
    proc.registers.b = 0xF;
    proc.registers.f = 0;
    Z80Clocks_t clocks = INC_reg(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 0x10);
    TESTME_ASSERT_INT_EQ(proc.registers.f, Z80_HALF_CARRY);
}
TESTME_END

TESTME_SUITE(test_z80_increment)
{
    TESTME_SUITE_RUN_TEST(test_z80_inc_16bit);
    TESTME_SUITE_RUN_TEST(test_z80_inc_reg_zero);
    TESTME_SUITE_RUN_TEST(test_z80_inc_reg_not_zero);
    TESTME_SUITE_RUN_TEST(test_z80_inc_reg_half_carry);
}
TESTME_SUITE_END
