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
Z80Clocks_t LD_16bit_imm(pZ80_t, uint8_t*, uint8_t*);
Z80Clocks_t LD_16bit_ind_reg(pZ80_t, uint8_t*, uint8_t*, uint8_t*);
Z80Clocks_t LD_reg_imm(pZ80_t, uint8_t*);
Z80Clocks_t INC_16bit(pZ80_t, uint8_t*, uint8_t*);
Z80Clocks_t INC_reg(pZ80_t, uint8_t*);
Z80Clocks_t DEC_reg(pZ80_t, uint8_t*);
Z80Clocks_t RLC_reg(pZ80_t, uint8_t*);
Z80Clocks_t ADD_HL_16bit(pZ80_t, uint8_t*, uint8_t*);

/* 0x0 */
Z80Clocks_t NOP(pZ80_t);
Z80Clocks_t LD_BC_imm(pZ80_t);
Z80Clocks_t LD_BC_ind_A(pZ80_t);
Z80Clocks_t INC_BC(pZ80_t);
Z80Clocks_t INC_B(pZ80_t);
Z80Clocks_t DEC_B(pZ80_t);
Z80Clocks_t LD_B_imm(pZ80_t);
Z80Clocks_t RLC_A(pZ80_t);
Z80Clocks_t LD_imm_SP(pZ80_t);
Z80CLocks_t ADD_HL_BC(pZ80_t);
Z80Clocks_t LD_A_BC_ind(pZ80_t);
Z80Clocks_t DEC_BC(pZ80_t);
Z80Clocks_t INC_C(pZ80_t);
Z80Clocks_t DEC_C(pZ80_t);
Z80Clocks_t LD_C_imm(pZ80_t);
Z80Clocks_t RRC_A(pZ80_t);
/* 0x1 */
Z80Clocks_t STOP0(pZ80_t);
Z80Clocks_t LD_DE_imm(pZ80_t);
Z80Clocks_t LD_DE_ind_A(pZ80_t);
Z80Clocks_t INC_DE(pZ80_t);
Z80Clocks_t INC_D(pZ80_t);
Z80Clocks_t DEC_D(pZ80_t);
Z80Clocks_t LD_D_imm(pZ80_t);
Z80Clocks_t RL_A(pZ80_t);
Z80Clocks_t JR_imm(pZ80_t);
Z80CLocks_t ADD_HL_DE(pZ80_t);
Z80Clocks_t LD_A_DE_ind(pZ80_t);
Z80Clocks_t DEC_DE(pZ80_t);
Z80Clocks_t INC_E(pZ80_t);
Z80Clocks_t DEC_E(pZ80_t);
Z80Clocks_t LD_E_imm(pZ80_t);
Z80Clocks_t RR_A(pZ80_t);
/* 0x2 */
Z80Clocks_t JR_NZ_imm(pZ80_t);
Z80Clocks_t LD_HL_imm(pZ80_t);
Z80Clocks_t LD_HL_ind_inc_A(pZ80_t);
Z80Clocks_t INC_HL(pZ80_t);
Z80Clocks_t INC_H(pZ80_t);
Z80Clocks_t DEC_H(pZ80_t);
Z80Clocks_t LD_H_imm(pZ80_t);
Z80Clocks_t DA_A(pZ80_t);
Z80Clocks_t JR_Z_imm(pZ80_t);
Z80CLocks_t ADD_HL_HL(pZ80_t);
Z80Clocks_t LD_A_HL_ind_inc(pZ80_t);
Z80Clocks_t DEC_HL(pZ80_t);
Z80Clocks_t INC_L(pZ80_t);
Z80Clocks_t DEC_L(pZ80_t);
Z80Clocks_t LD_L_imm(pZ80_t);
Z80Clocks_t CPL_A(pZ80_t);
/* 0x3 */
Z80Clocks_t JR_NC_imm(pZ80_t);
Z80Clocks_t LD_SP_imm(pZ80_t);
Z80Clocks_t LD_HL_ind_dec_A(pZ80_t);
Z80Clocks_t INC_SP(pZ80_t);
Z80Clocks_t INC_HL_ind(pZ80_t);
Z80Clocks_t DEC_HL_ind(pZ80_t);
Z80Clocks_t LD_HL_ind_imm(pZ80_t);
Z80Clocks_t SCF(pZ80_t);
Z80Clocks_t JR_C_imm(pZ80_t);
Z80CLocks_t ADD_HL_SL(pZ80_t);
Z80Clocks_t LD_A_HL_ind_dec(pZ80_t);
Z80Clocks_t DEC_SP(pZ80_t);
Z80Clocks_t INC_A(pZ80_t);
Z80Clocks_t DEC_A(pZ80_t);
Z80Clocks_t LD_A_imm(pZ80_t);
Z80Clocks_t CCF(pZ80_t);
/* 0x4 */
Z80Clocks_t LD_B_B(pZ80_t);
Z80Clocks_t LD_B_C(pZ80_t);
Z80Clocks_t LD_B_D(pZ80_t);
Z80Clocks_t LD_B_E(pZ80_t);
Z80Clocks_t LD_B_H(pZ80_t);
Z80Clocks_t LD_B_L(pZ80_t);
Z80Clocks_t LD_B_HL_ind(pZ80_t);
Z80Clocks_t LD_B_A(pZ80_t);
Z80Clocks_t LD_C_B(pZ80_t);
Z80CLocks_t LD_C_C(pZ80_t);
Z80Clocks_t LD_C_D(pZ80_t);
Z80Clocks_t LD_C_E(pZ80_t);
Z80Clocks_t LD_C_H(pZ80_t);
Z80Clocks_t LD_C_L(pZ80_t);
Z80Clocks_t LD_C_HL_ind(pZ80_t);
Z80Clocks_t LD_C_A(pZ80_t);
/* 0x5 */
Z80Clocks_t LD_D_B(pZ80_t);
Z80Clocks_t LD_D_C(pZ80_t);
Z80Clocks_t LD_D_D(pZ80_t);
Z80Clocks_t LD_D_E(pZ80_t);
Z80Clocks_t LD_D_H(pZ80_t);
Z80Clocks_t LD_D_L(pZ80_t);
Z80Clocks_t LD_D_HL_ind(pZ80_t);
Z80Clocks_t LD_D_A(pZ80_t);
Z80Clocks_t LD_E_B(pZ80_t);
Z80CLocks_t LD_E_C(pZ80_t);
Z80Clocks_t LD_E_D(pZ80_t);
Z80Clocks_t LD_E_E(pZ80_t);
Z80Clocks_t LD_E_H(pZ80_t);
Z80Clocks_t LD_E_L(pZ80_t);
Z80Clocks_t LD_E_HL_ind(pZ80_t);
Z80Clocks_t LD_E_A(pZ80_t);
/* 0x6 */
Z80Clocks_t LD_H_B(pZ80_t);
Z80Clocks_t LD_H_C(pZ80_t);
Z80Clocks_t LD_H_D(pZ80_t);
Z80Clocks_t LD_H_E(pZ80_t);
Z80Clocks_t LD_H_H(pZ80_t);
Z80Clocks_t LD_H_L(pZ80_t);
Z80Clocks_t LD_H_HL_ind(pZ80_t);
Z80Clocks_t LD_H_A(pZ80_t);
Z80Clocks_t LD_L_B(pZ80_t);
Z80CLocks_t LD_L_C(pZ80_t);
Z80Clocks_t LD_L_D(pZ80_t);
Z80Clocks_t LD_L_E(pZ80_t);
Z80Clocks_t LD_L_H(pZ80_t);
Z80Clocks_t LD_L_L(pZ80_t);
Z80Clocks_t LD_L_HL_ind(pZ80_t);
Z80Clocks_t LD_L_A(pZ80_t);
/* 0x7 */
Z80Clocks_t LD_HL_ind_B(pZ80_t);
Z80Clocks_t LD_HL_ind_C(pZ80_t);
Z80Clocks_t LD_HL_ind_D(pZ80_t);
Z80Clocks_t LD_HL_ind_E(pZ80_t);
Z80Clocks_t LD_HL_H(pZ80_t);
Z80Clocks_t LD_HL_L(pZ80_t);
Z80Clocks_t HALT(pZ80_t);
Z80Clocks_t LD_HL_A(pZ80_t);
Z80Clocks_t LD_A_B(pZ80_t);
Z80CLocks_t LD_A_C(pZ80_t);
Z80Clocks_t LD_A_D(pZ80_t);
Z80Clocks_t LD_A_E(pZ80_t);
Z80Clocks_t LD_A_H(pZ80_t);
Z80Clocks_t LD_A_L(pZ80_t);
Z80Clocks_t LD_A_HL_ind(pZ80_t);
Z80Clocks_t LD_A_A(pZ80_t);
/* 0x8 */
Z80Clocks_t ADD_A_B(pZ80_t);
Z80Clocks_t ADD_A_C(pZ80_t);
Z80Clocks_t ADD_A_D(pZ80_t);
Z80Clocks_t ADD_A_E(pZ80_t);
Z80Clocks_t ADD_A_H(pZ80_t);
Z80Clocks_t ADD_A_L(pZ80_t);
Z80Clocks_t ADD_A_HL_ind(pZ80_t);
Z80Clocks_t ADD_A_A(pZ80_t);
Z80Clocks_t ADC_A_B(pZ80_t);
Z80Clocks_t ADC_A_C(pZ80_t);
Z80Clocks_t ADC_A_D(pZ80_t);
Z80Clocks_t ADC_A_E(pZ80_t);
Z80Clocks_t ADC_A_H(pZ80_t);
Z80Clocks_t ADC_A_L(pZ80_t);
Z80Clocks_t ADC_A_HL_ind(pZ80_t);
Z80Clocks_t ADC_A_A(pZ80_t);
/* 0x9 */
Z80Clocks_t SUB_A_B(pZ80_t);
Z80Clocks_t SUB_A_C(pZ80_t);
Z80Clocks_t SUB_A_D(pZ80_t);
Z80Clocks_t SUB_A_E(pZ80_t);
Z80Clocks_t SUB_A_H(pZ80_t);
Z80Clocks_t SUB_A_L(pZ80_t);
Z80Clocks_t SUB_A_HL_ind(pZ80_t);
Z80Clocks_t SUB_A_A(pZ80_t);
Z80Clocks_t SBC_A_B(pZ80_t);
Z80Clocks_t SBC_A_C(pZ80_t);
Z80Clocks_t SBC_A_D(pZ80_t);
Z80Clocks_t SBC_A_E(pZ80_t);
Z80Clocks_t SBC_A_H(pZ80_t);
Z80Clocks_t SBC_A_L(pZ80_t);
Z80Clocks_t SBC_A_HL_ind(pZ80_t);
Z80Clocks_t SBC_A_A(pZ80_t);
/* 0xA */
Z80Clocks_t AND_A_B(pZ80_t);
Z80Clocks_t AND_A_C(pZ80_t);
Z80Clocks_t AND_A_D(pZ80_t);
Z80Clocks_t AND_A_E(pZ80_t);
Z80Clocks_t AND_A_H(pZ80_t);
Z80Clocks_t AND_A_L(pZ80_t);
Z80Clocks_t AND_A_HL_ind(pZ80_t);
Z80Clocks_t AND_A_A(pZ80_t);
Z80Clocks_t XOR_A_B(pZ80_t);
Z80Clocks_t XOR_A_C(pZ80_t);
Z80Clocks_t XOR_A_D(pZ80_t);
Z80Clocks_t XOR_A_E(pZ80_t);
Z80Clocks_t XOR_A_H(pZ80_t);
Z80Clocks_t XOR_A_L(pZ80_t);
Z80Clocks_t XOR_A_HL_ind(pZ80_t);
Z80Clocks_t XOR_A_A(pZ80_t);
/* 0xB */
Z80Clocks_t OR_A_B(pZ80_t);
Z80Clocks_t OR_A_C(pZ80_t);
Z80Clocks_t OR_A_D(pZ80_t);
Z80Clocks_t OR_A_E(pZ80_t);
Z80Clocks_t OR_A_H(pZ80_t);
Z80Clocks_t OR_A_L(pZ80_t);
Z80Clocks_t OR_A_HL_ind(pZ80_t);
Z80Clocks_t OR_A_A(pZ80_t);
Z80Clocks_t CP_A_B(pZ80_t);
Z80Clocks_t CP_A_C(pZ80_t);
Z80Clocks_t CP_A_D(pZ80_t);
Z80Clocks_t CP_A_E(pZ80_t);
Z80Clocks_t CP_A_H(pZ80_t);
Z80Clocks_t CP_A_L(pZ80_t);
Z80Clocks_t CP_A_HL_ind(pZ80_t);
Z80Clocks_t CP_A_A(pZ80_t);
/* 0xC */
Z80Clocks_t RET_NZ(pZ80_t);
Z80Clocks_t POP_BC(pZ80_t);
Z80Clocks_t JP_NZ_imm(pZ80_t);
Z80Clocks_t JP_imm(pZ80_t);
Z80Clocks_t CALL_NZ_imm(pZ80_t);
Z80Clocks_t PUSH_BC(pZ80_t);
Z80Clocks_t ADD_A_imm(pZ80_t);
Z80Clocks_t RST_00(pZ80_t);
Z80Clocks_t RET_Z(pZ80_t);
Z80Clocks_t RET(pZ80_t);
Z80Clocks_t JP_Z_imm(pZ80_t);
Z80Clocks_t EXTRA_OPS(pZ80_t);
Z80Clocks_t CALL_Z_imm(pZ80_t);
Z80Clocks_t CALL_imm(pZ80_t);
Z80Clocks_t ADC_A_imm(pZ80_t);
Z80Clocks_t RST_08(pZ80_t);
/* 0xD */
Z80Clocks_t RET_NC(pZ80_t);
Z80Clocks_t POP_DE(pZ80_t);
Z80Clocks_t JP_NC_imm(pZ80_t);
/*nop*/
Z80Clocks_t CALL_NC_imm(pZ80_t);
Z80Clocks_t PUSH_DE(pZ80_t);
Z80Clocks_t SUB_A_imm(pZ80_t);
Z80Clocks_t RST_10(pZ80_t);
Z80Clocks_t RET_C(pZ80_t);
Z80Clocks_t RETI(pZ80_t);
Z80Clocks_t JP_C_imm(pZ80_t);
/*nop*/
Z80Clocks_t CALL_C_imm(pZ80_t);
/*nop*/
Z80Clocks_t SBC_A_imm(pZ80_t);
Z80Clocks_t RST_18(pZ80_t);
/* 0xE */
Z80Clocks_t LDH_imm_A(pZ80_t);
Z80Clocks_t POP_HL(pZ80_t);
Z80Clocks_t LD_C_ind_A(pZ80_t);
/*nop*/
/*nop*/
Z80Clocks_t PUSH_HL(pZ80_t);
Z80Clocks_t AND_A_imm(pZ80_t);
Z80Clocks_t RST_20(pZ80_t);
Z80Clocks_t ADD_SP_imm(pZ80_t);
Z80Clocks_t JP_HL(pZ80_t);
Z80Clocks_t LD_imm_ind_A(pZ80_t);
/*nop*/
/*nop*/
/*nop*/
Z80Clocks_t XOR_A_imm(pZ80_t);
Z80Clocks_t RST_28(pZ80_t);
/* 0xF */
Z80Clocks_t LDH_A_imm(pZ80_t);
Z80Clocks_t POP_AF(pZ80_t);
Z80Clocks_t LD_A_C_ind(pZ80_t);
Z80Clocks_t DI(pZ80_t);
/*nop*/
Z80Clocks_t PUSH_AF(pZ80_t);
Z80Clocks_t OR_A_imm(pZ80_t);
Z80Clocks_t RST_30(pZ80_t);
Z80Clocks_t LD_HL_SP_imm(pZ80_t);
Z80Clocks_t LD_SP_HL(pZ80_t);
Z80Clocks_t LD_A_imm_ind(pZ80_t);
Z80Clocks_t EI(pZ80_t);
/*nop*/
/*nop*/
Z80Clocks_t CP_A_imm(pZ80_t);
Z80Clocks_t RST_38(pZ80_t);

#endif
