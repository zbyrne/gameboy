#include <stdint.h>
#include "z80.h"

extern uint8_t mem_read(uint16_t);
extern void mem_write(uint16_t, uint8_t);

/*
 * Reset the z80 struct to power on state.
 */
void
z80_reset(pZ80_t proc)
{
    proc->registers.a = 0;
    proc->registers.b = 0;
    proc->registers.c = 0;
    proc->registers.d = 0;
    proc->registers.e = 0;
    proc->registers.h = 0;
    proc->registers.l = 0;
    proc->registers.f = 0;
    proc->registers.pc = 0;
    proc->registers.sp = 0;
    proc->registers.ime = 1;
    proc->clocks.m = 0;
    proc->clocks.t = 0;
}

/*
 * Helper Functions for setting or clearing status flags.
 */
void
z80_set_flag(pZ80_t proc, uint8_t condition, uint8_t flag)
{
    if (condition)
    {
        proc->registers.f |= flag;
    }
    else
    {
        proc->registers.f &= ~flag;
    }
}

void
z80_set_zero(pZ80_t proc, uint8_t condition)
{
    z80_set_flag(proc, condition, Z80_ZERO);
}

void
z80_set_sub_op(pZ80_t proc, uint8_t condition)
{
    z80_set_flag(proc, condition, Z80_SUB_OP);
}

void
z80_set_half_carry(pZ80_t proc, uint8_t condition)
{
    z80_set_flag(proc, condition, Z80_HALF_CARRY);
}

void
z80_set_carry(pZ80_t proc, uint8_t condition)
{
    z80_set_flag(proc, condition, Z80_CARRY);
}

/*
 * Do nothing, and increment the clocks.
 */
Z80Clocks_t
NOP(pZ80_t proc)
{
    Z80Clocks_t rtn = {1, 4};
    return rtn;
}

/*
 * Load 16-bit immediate value into BC
 */
Z80Clocks_t
LD_BC_imm(pZ80_t proc)
{
    proc->registers.b = mem_read(++proc->registers.pc);
    proc->registers.c = mem_read(++proc->registers.pc);
    Z80Clocks_t rtn = {3, 12};
    return rtn;
}

/*
 * Load value in A into address in BC
 */
Z80Clocks_t
LD_BC_ind_A(pZ80_t proc)
{
    uint16_t addr = (proc->registers.b << 8) + proc->registers.c;
    mem_write(addr, proc->registers.a);
    Z80Clocks_t rtn = {2, 8};
    return rtn;
}

/*
 * Increment the value of BC
 */
Z80Clocks_t
INC_BC(pZ80_t proc)
{
    uint16_t val = (proc->registers.b << 8) + proc->registers.c + 1;
    proc->registers.b = (val >> 8) & 0xFF;
    proc->registers.c = val & 0xFF;
    Z80Clocks_t rtn = {2, 8};
    return rtn;
}

/*
 * Increment the value of B
 */
Z80Clocks_t
INC_B(pZ80_t proc)
{
    uint8_t val = proc->registers.b + 1;
    z80_set_sub_op(proc, 0);
    z80_set_zero(proc, (val == 0 ? 1 : 0));
    z80_set_half_carry(proc, ((proc->registers.b & 0xF) + 1 >= 0x10 ? 1 : 0));
    proc->registers.b = val;
    Z80Clocks_t rtn = {1, 4};
    return rtn;
}

/*
 * Decrement the value of B
 */
Z80Clocks_t
DEC_B(pZ80_t proc)
{
    uint8_t val = proc->registers.b - 1;
    z80_set_sub_op(proc, 1);
    z80_set_zero(proc, (val == 0 ? 1 : 0));
    z80_set_half_carry(proc, ((proc->registers.b & 0xF0) > (val & 0xF0) ? 1 : 0));
    proc->registers.b = val;
    Z80Clocks_t rtn = {1, 4};
    return rtn;
}

/*
 * Load 8-bit immediate value into B
 */
Z80Clocks_t
LD_B_imm(pZ80_t proc)
{
    proc->registers.b = mem_read(++proc->registers.pc);
    Z80Clocks_t rtn = {2, 8};
    return rtn;
}

/*
 * Rotate A left with carry.
 */
Z80Clocks_t
RLC_A(pZ80_t proc)
{
    uint8_t carry = proc->registers.a & 0x80 ? 1 : 0;
    uint8_t val = (proc->registers.a << 1) + carry;
    z80_set_sub_op(proc, 0);
    z80_set_zero(proc, (val == 0 ? 1 : 0));
    z80_set_half_carry(proc, 0);
    z80_set_carry(proc, carry);
    proc->registers.a = val;
    Z80Clocks_t rtn = {1, 4};
    return rtn;
}
