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
} Z80Registers, *pZ80Registers;

/* Clock Type */
typedef struct{
  uint16_t m;
  uint16_t t;
} Z80Clocks, *pZ80Clocks;

/* Processor Type */
typedef struct{
  Z80Registers registers;
  Z80Clocks clocks;
} Z80_t, *pZ80_t;

/* Status Register Masks */
#define Z80_ZERO 0x80
#define Z80_SUB_OP 0x40
#define Z80_HALF_CARRY 0x20
#define Z80_CARRY 0x10

/* Function Definitions */
void z80_reset(pZ80_t proc);
void z80_decode(pZ80_t proc);

#endif
