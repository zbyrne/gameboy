#include <stdint.h>
#include "z80.h"

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
    /* TODO: load value from memory @ pc */
    /* TODO: increment program counter */
    Z80Clocks_t rtn = {3, 12};
    return rtn;
}
