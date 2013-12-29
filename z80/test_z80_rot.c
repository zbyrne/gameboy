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

START_TEST(test_z80_rlc_a_zero)
{
    Z80_t proc;
    proc.registers.a = 0x0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = RLC_A(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.a, 0);
    ck_assert_int_eq(proc.registers.f, Z80_ZERO);
}
END_TEST

START_TEST(test_z80_rlc_a_set_carry)
{
    Z80_t proc;
    proc.registers.a = 0xF0;
    proc.registers.f = 0;
    Z80Clocks_t clocks = RLC_A(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.a, 0xE1);
    ck_assert_int_eq(proc.registers.f, Z80_CARRY);
}
END_TEST

START_TEST(test_z80_rlc_a_clear_carry)
{
    Z80_t proc;
    proc.registers.a = 0xF;
    proc.registers.f = Z80_CARRY;
    Z80Clocks_t clocks = RLC_A(&proc);
    ck_assert_int_eq(clocks.m, 1);
    ck_assert_int_eq(clocks.t, 4);
    ck_assert_int_eq(proc.registers.a, 0x1E);
    ck_assert_int_eq(proc.registers.f, 0);
}
END_TEST

Suite *
z80_rot_suite(void)
{
    Suite *s = suite_create("z80_Rotate");
    TCase *tc_core = tcase_create("Core");
/*
  And are added here, like this
    tcase_add_test(tc_core, test_z80_reset);
 */
    tcase_add_test(tc_core, test_z80_rlc_a_zero);
    tcase_add_test(tc_core, test_z80_rlc_a_set_carry);
    tcase_add_test(tc_core, test_z80_rlc_a_clear_carry);
    suite_add_tcase(s, tc_core);
    return s;
}

int
main(void)
{
    int number_failed;
    Suite *s = z80_rot_suite();
    SRunner *sr = srunner_create(s);
    srunner_run_all(sr, CK_NORMAL);
    number_failed = srunner_ntests_failed(sr);
    srunner_free(sr);
    return number_failed;
}
