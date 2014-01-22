#include <stdint.h>
#include <check.h>
#include <string.h>
#include "z80.h"

/*Tests look like this
START_TEST(dummy_test)
{
    ck_assert_int_eq(5, 5);
}
END_TEST
*/

START_TEST(test_z80_reset)
{
    Z80_t proc;
    memset(&proc, 0xFF, sizeof(proc));
    z80_reset(&proc);
    ck_assert_int_eq(proc.registers.a, 0);
    ck_assert_int_eq(proc.registers.b, 0);
    ck_assert_int_eq(proc.registers.c, 0);
    ck_assert_int_eq(proc.registers.d, 0);
    ck_assert_int_eq(proc.registers.e, 0);
    ck_assert_int_eq(proc.registers.f, 0);
    ck_assert_int_eq(proc.registers.pc, 0);
    ck_assert_int_eq(proc.registers.sp, 0);
    ck_assert_int_eq(proc.registers.ime, 1);
    ck_assert_int_eq(proc.clocks.m, 0);
    ck_assert_int_eq(proc.clocks.t, 0);
}
END_TEST

START_TEST(test_nop)
{
    Z80_t proc;
    Z80Clocks_t clocks = NOP(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
}
END_TEST

uint8_t
mem_read(uint16_t addr)
{
    return 0xF0 + addr;
}

START_TEST(test_ld_16bit_imm)
{
    Z80_t proc;
    proc.registers.b = 0;
    proc.registers.c = 0;
    proc.registers.pc = 0;
    Z80Clocks_t clocks = LD_16bit_imm(&proc, &proc.registers.b,
                                      &proc.registers.c);
    ck_assert_int_eq(clocks.m, 3);
    ck_assert_int_eq(clocks.t, 12);
    uint16_t result = (proc.registers.b << 8) + proc.registers.c;
    ck_assert_int_eq(result, 0xF1F2);
    ck_assert_int_eq(proc.registers.pc, 2);
}
END_TEST

uint8_t ram[1024] = {0};

void
mem_write(uint16_t addr, uint8_t val)
{
    ram[addr] = val;
}

START_TEST(test_ld_16bit_ind_reg)
{
    Z80_t proc;
    proc.registers.a = 0xAA;
    proc.registers.b = 0x1;
    proc.registers.c = 0xC;
    proc.registers.pc = 0;
    Z80Clocks_t clocks = LD_16bit_ind_reg(&proc, &proc.registers.b,
                                          &proc.registers.c, &proc.registers.a);
    ck_assert_int_eq(clocks.m, 2);
    ck_assert_int_eq(clocks.t, 8);
    ck_assert_int_eq(ram[0x10C], 0xAA);
    ck_assert_int_eq(proc.registers.pc, 0);
}
END_TEST

START_TEST(test_ld_b_imm)
{
    Z80_t proc;
    proc.registers.b = 0;
    proc.registers.pc = 0;
    Z80Clocks_t clocks = LD_B_imm(&proc);
    ck_assert_int_eq(clocks.m, 2);
    ck_assert_int_eq(clocks.t, 8);
    ck_assert_int_eq(proc.registers.b, 0xF1);
    ck_assert_int_eq(proc.registers.pc, 1);
}
END_TEST

Suite *
z80_ld_suite(void)
{
    Suite *s = suite_create("z80_Load");
    TCase *tc_core = tcase_create("Core");
/*
  And are added here, like this
    tcase_add_test(tc_core, test_z80_reset);
 */
    tcase_add_test(tc_core, test_z80_reset);
    tcase_add_test(tc_core, test_nop);
    tcase_add_test(tc_core, test_ld_16bit_imm);
    tcase_add_test(tc_core, test_ld_16bit_ind_reg);
    tcase_add_test(tc_core, test_ld_b_imm);
    suite_add_tcase(s, tc_core);
    return s;
}

int
main(void)
{
    int number_failed;
    Suite *s = z80_ld_suite();
    SRunner *sr = srunner_create(s);
    srunner_run_all(sr, CK_NORMAL);
    number_failed = srunner_ntests_failed(sr);
    srunner_free(sr);
    return number_failed;
}
