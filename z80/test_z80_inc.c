#include <stdint.h>
#include <check.h>
#include <string.h>
#include "z80.h"

uint8_t mem_read(uint16_t addr){return 0;}
void mem_write(uint16_t addr, uint8_t val){}


/*Tests look like this
START_TEST(dummy_test)
{
    ck_assert_int_eq(5, 5);
}
END_TEST
*/

START_TEST(test_z80_inc_16bit)
{
    Z80_t proc;
    proc.registers.b = 1;
    proc.registers.c = 0xFF;
    Z80Clocks_t clocks = INC_16bit(&proc, &proc.registers.b, &proc.registers.c);
    ck_assert_int_eq(clocks.m, 2);
    ck_assert_int_eq(clocks.t, 8);
    uint16_t result = (proc.registers.b << 8) + proc.registers.c;
    ck_assert_int_eq(result, 0x200);
}
END_TEST

START_TEST(test_z80_inc_reg_zero)
{
    Z80_t proc;
    proc.registers.b = 0xFF;
    proc.registers.f = 0;
    Z80Clocks_t clocks = INC_reg(&proc, &proc.registers.b);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.b, 0);
    /* 0xFF + 1 does indeed half-carry */
    ck_assert_int_eq(proc.registers.f, Z80_ZERO | Z80_HALF_CARRY);
}
END_TEST

START_TEST(test_z80_inc_reg_not_zero)
{
    Z80_t proc;
    proc.registers.b = 5;
    proc.registers.f = 0;
    Z80Clocks_t clocks = INC_reg(&proc, &proc.registers.b);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.b, 6);
    ck_assert_int_eq(proc.registers.f, 0);
}
END_TEST

START_TEST(test_z80_inc_reg_half_carry)
{
    Z80_t proc;
    proc.registers.b = 0xF;
    proc.registers.f = 0;
    Z80Clocks_t clocks = INC_reg(&proc, &proc.registers.b);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.b, 0x10);
    ck_assert_int_eq(proc.registers.f, Z80_HALF_CARRY);
}
END_TEST

Suite *
z80_inc_suite(void)
{
    Suite *s = suite_create("z80_Increment");
    TCase *tc_core = tcase_create("Core");
/*
  And are added here, like this
    tcase_add_test(tc_core, test_z80_reset);
 */
    tcase_add_test(tc_core, test_z80_inc_16bit);
    tcase_add_test(tc_core, test_z80_inc_reg_zero);
    tcase_add_test(tc_core, test_z80_inc_reg_not_zero);
    tcase_add_test(tc_core, test_z80_inc_reg_half_carry);
    suite_add_tcase(s, tc_core);
    return s;
}

int
main(void)
{
    int number_failed;
    Suite *s = z80_inc_suite();
    SRunner *sr = srunner_create(s);
    srunner_run_all(sr, CK_NORMAL);
    number_failed = srunner_ntests_failed(sr);
    srunner_free(sr);
    return number_failed;
}
