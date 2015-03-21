#include <stdint.h>
#include <string.h>
#include "z80.h"
#include "testme.h"

uint8_t mem_read(uint16_t addr){return 0;}
void mem_write(uint16_t addr, uint8_t val){}

TESTME_START(test_z80_dec_reg_zero)
{
    Z80_t proc;
    proc.registers.b = 0x01;
    proc.registers.f = 0;
    Z80Clocks_t clocks = DEC_reg(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 0);
    uint8_t flags = Z80_ZERO | Z80_SUB_OP;
    TESTME_ASSERT_INT_EQ(proc.registers.f, flags);
}
TESTME_END

TESTME_START(test_z80_dec_reg_not_zero)
{
    Z80_t proc;
    proc.registers.b = 5;
    proc.registers.f = 0;
    Z80Clocks_t clocks = DEC_reg(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.f, Z80_SUB_OP);
}
TESTME_END

TESTME_START(test_z80_dec_reg_half_carry)
{
    Z80_t proc;
    proc.registers.b = 0xF0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = DEC_reg(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 0xEF);
    uint8_t flags = Z80_HALF_CARRY | Z80_SUB_OP;
    TESTME_ASSERT_INT_EQ(proc.registers.f, flags);
}
TESTME_END

TESTME_SUITE(test_z80_decrement)
{
    TESTME_SUITE_RUN_TEST(test_z80_dec_reg_zero);
    TESTME_SUITE_RUN_TEST(test_z80_dec_reg_not_zero);
    TESTME_SUITE_RUN_TEST(test_z80_dec_reg_half_carry);
}
TESTME_SUITE_END
