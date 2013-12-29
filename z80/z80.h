#ifndef Z80_H
#define Z80_H

/* Register type */
typedef struct{
  uint8_t a;
  uint8_t b;
  uint8_t c;
  uint8_t d;
  uint8_t e;
  uint8_t h;
  uint8_t l;
  uint8_t f;
  uint16_t pc;
  uint16_t sp;
  uint8_t ime;
} Z80Registers_t, *pZ80Registers_t;

/* Clock Type */
typedef struct{
  uint16_t m;
  uint16_t t;
} Z80Clocks_t, *pZ80Clocks_t;

/* Processor Type */
typedef struct{
  Z80Registers_t registers;
  Z80Clocks_t clocks;
} Z80_t, *pZ80_t;

/* Status Register Masks */
#define Z80_ZERO 0x80
#define Z80_SUB_OP 0x40
#define Z80_HALF_CARRY 0x20
#define Z80_CARRY 0x10

/* Function Definitions */
void z80_reset(pZ80_t);
void z80_decode(pZ80_t);
void z80_set_flag(pZ80_t, uint8_t, uint8_t);
void z80_set_zero(pZ80_t, uint8_t);
void z80_set_sub_op(pZ80_t, uint8_t);
void z80_set_half_carry(pZ80_t, uint8_t);
void z80_set_carry(pZ80_t, uint8_t);

/* Opcode Function Definitions */
/* 0x0 */
Z80Clocks_t NOP(pZ80_t);
Z80Clocks_t LD_BC_imm(pZ80_t);
Z80Clocks_t LD_BC_ind_A(pZ80_t);
Z80Clocks_t INC_BC(pZ80_t);
Z80Clocks_t INC_B(pZ80_t);
Z80Clocks_t DEC_B(pZ80_t);
Z80Clocks_t LD_B_imm(pZ80_t);
Z80Clocks_t RLC_A(pZ80_t);
/* 0x1 */
/* 0x2 */
/* 0x3 */
/* 0x4 */
/* 0x5 */
/* 0x6 */
/* 0x7 */
/* 0x8 */
/* 0x9 */
/* 0xA */
/* 0xB */
/* 0xC */
/* 0xD */
/* 0xE */
/* 0xF */

#endif
