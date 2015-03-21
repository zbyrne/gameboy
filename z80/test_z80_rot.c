#include <stdint.h>
#include <string.h>
#include "z80.h"
#include "testme.h"

uint8_t mem_read(uint16_t addr){return 0;}
void mem_write(uint16_t addr, uint8_t val){}

TESTME_START(test_z80_rlc_reg_zero)
{
    Z80_t proc;
    proc.registers.a = 0x0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = RLC_reg(&proc, &proc.registers.a);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.a, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.f, Z80_ZERO);
}
TESTME_END

TESTME_START(test_z80_rlc_reg_set_carry)
{
    Z80_t proc;
    proc.registers.a = 0xF0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = RLC_reg(&proc, &proc.registers.a);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.a, 0xE1);
    TESTME_ASSERT_INT_EQ(proc.registers.f, Z80_CARRY);
}
TESTME_END

TESTME_START(test_z80_rlc_reg_clear_carry)
{
    Z80_t proc;
    proc.registers.a = 0xF;
    proc.registers.f = Z80_CARRY;
    Z80Clocks_t clocks = RLC_reg(&proc, &proc.registers.a);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
    TESTME_ASSERT_INT_EQ(proc.registers.a, 0x1E);
    TESTME_ASSERT_INT_EQ(proc.registers.f, 0);
}
TESTME_END

TESTME_SUITE(test_z80_rotate)
{
    TESTME_SUITE_RUN_TEST(test_z80_rlc_reg_zero);
    TESTME_SUITE_RUN_TEST(test_z80_rlc_reg_set_carry);
    TESTME_SUITE_RUN_TEST(test_z80_rlc_reg_clear_carry);
}
TESTME_SUITE_END
