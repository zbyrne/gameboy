#include <stdint.h>
#include <string.h>
#include "z80.h"
#include "testme.h"

TESTME_START(test_z80_reset)
{
    Z80_t proc;
    memset(&proc, 0xFF, sizeof(proc));
    z80_reset(&proc);
    TESTME_ASSERT_INT_EQ(proc.registers.a, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.c, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.d, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.e, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.f, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.pc, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.sp, 0);
    TESTME_ASSERT_INT_EQ(proc.registers.ime, 1);
    TESTME_ASSERT_INT_EQ(proc.clocks.m, 0);
    TESTME_ASSERT_INT_EQ(proc.clocks.t, 0);
}
TESTME_END

TESTME_START(test_nop)
{
    Z80_t proc;
    Z80Clocks_t clocks = NOP(&proc);
    TESTME_ASSERT_INT_EQ(clocks.m, 1);
    TESTME_ASSERT_INT_EQ(clocks.t, 4);
}
TESTME_END

uint8_t ram[1024] = {0};

void
mem_write(uint16_t addr, uint8_t val)
{
    ram[addr] = val;
}

uint8_t
mem_read(uint16_t addr)
{
    return ram[addr];
}

TESTME_START(test_ld_16bit_imm)
{
    Z80_t proc;
    memset(ram, 0, sizeof(ram));
    proc.registers.b = 0;
    proc.registers.c = 0;
    proc.registers.pc = 0;
    ram[1] = 1;
    ram[2] = 2;
    Z80Clocks_t clocks = LD_16bit_imm(&proc, &proc.registers.b,
                                      &proc.registers.c);
    TESTME_ASSERT_INT_EQ(clocks.m, 3);
    TESTME_ASSERT_INT_EQ(clocks.t, 12);
    uint16_t result = (proc.registers.b << 8) + proc.registers.c;
    TESTME_ASSERT_INT_EQ(result, 0x201);
    TESTME_ASSERT_INT_EQ(proc.registers.pc, 2);
}
TESTME_END

TESTME_START(test_ld_16bit_ind_reg)
{
    Z80_t proc;
    memset(ram, 0, sizeof(ram));
    proc.registers.a = 0xAA;
    proc.registers.b = 0x1;
    proc.registers.c = 0xC;
    proc.registers.pc = 0;
    Z80Clocks_t clocks = LD_16bit_ind_reg(&proc, &proc.registers.b,
                                          &proc.registers.c, &proc.registers.a);
    TESTME_ASSERT_INT_EQ(clocks.m, 2);
    TESTME_ASSERT_INT_EQ(clocks.t, 8);
    TESTME_ASSERT_INT_EQ(ram[0x10C], 0xAA);
    TESTME_ASSERT_INT_EQ(proc.registers.pc, 0);
}
TESTME_END

TESTME_START(test_ld_reg_imm)
{
    Z80_t proc;
    memset(ram, 0, sizeof(ram));
    proc.registers.b = 0;
    proc.registers.pc = 0;
    ram[1] = 1;
    Z80Clocks_t clocks = LD_reg_imm(&proc, &proc.registers.b);
    TESTME_ASSERT_INT_EQ(clocks.m, 2);
    TESTME_ASSERT_INT_EQ(clocks.t, 8);
    TESTME_ASSERT_INT_EQ(proc.registers.b, 1);
    TESTME_ASSERT_INT_EQ(proc.registers.pc, 1);
}
TESTME_END

TESTME_START(test_ld_imm_sp)
{
    Z80_t proc;
    memset(ram, 0, sizeof(ram));
    proc.registers.sp = 0x55AA;
    proc.registers.pc = 0;
    ram[1] = 1;
    ram[2] = 2;
    Z80Clocks_t clocks = LD_imm_SP(&proc);
    TESTME_ASSERT_INT_EQ(clocks.m, 5);
    TESTME_ASSERT_INT_EQ(clocks.t, 20);
    TESTME_ASSERT_INT_EQ(ram[0x201], 0xAA);
    TESTME_ASSERT_INT_EQ(ram[0x202], 0x55);
    TESTME_ASSERT_INT_EQ(proc.registers.pc, 2);
}
TESTME_END

TESTME_SUITE(z80_load)
{
    TESTME_SUITE_RUN_TEST(test_z80_reset);
    TESTME_SUITE_RUN_TEST(test_nop);
    TESTME_SUITE_RUN_TEST(test_ld_16bit_imm);
    TESTME_SUITE_RUN_TEST(test_ld_16bit_ind_reg);
    TESTME_SUITE_RUN_TEST(test_ld_reg_imm);
    TESTME_SUITE_RUN_TEST(test_ld_imm_sp);
}
TESTME_SUITE_END
