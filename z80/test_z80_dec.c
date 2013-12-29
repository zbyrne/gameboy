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

START_TEST(test_z80_dec_b_zero)
{
    Z80_t proc;
    proc.registers.b = 0x01;
    proc.registers.f = 0;
    Z80Clocks_t clocks = DEC_B(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.b, 0);
    ck_assert_int_eq(proc.registers.f, Z80_ZERO | Z80_SUB_OP);
}
END_TEST

START_TEST(test_z80_dec_b_not_zero)
{
    Z80_t proc;
    proc.registers.b = 5;
    proc.registers.f = 0;
    Z80Clocks_t clocks = DEC_B(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.b, 4);
    ck_assert_int_eq(proc.registers.f, Z80_SUB_OP);
}
END_TEST

START_TEST(test_z80_dec_b_half_carry)
{
    Z80_t proc;
    proc.registers.b = 0xF0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = DEC_B(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.b, 0xEF);
    ck_assert_int_eq(proc.registers.f, Z80_HALF_CARRY | Z80_SUB_OP);
}
END_TEST

Suite *
z80_dec_suite(void)
{
    Suite *s = suite_create("z80_Decrement");
    TCase *tc_core = tcase_create("Core");
/*
  And are added here, like this
    tcase_add_test(tc_core, test_z80_reset);
 */
    tcase_add_test(tc_core, test_z80_dec_b_zero);
    tcase_add_test(tc_core, test_z80_dec_b_not_zero);
    tcase_add_test(tc_core, test_z80_dec_b_half_carry);
    suite_add_tcase(s, tc_core);
    return s;
}

int
main(void)
{
    int number_failed;
    Suite *s = z80_dec_suite();
    SRunner *sr = srunner_create(s);
    srunner_run_all(sr, CK_NORMAL);
    number_failed = srunner_ntests_failed(sr);
    srunner_free(sr);
    return number_failed;
}
