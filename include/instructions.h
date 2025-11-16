#ifndef INST_H
#define INST_H

typedef enum {
  MOV_REG = 0x01,  MOV_IMM,
  LOAD, STORE_REG, STORE_IMM,

  ADD_REG, ADD_IMM,
  SUB_REG, SUB_IMM,
  MUL_REG, MUL_IMM,
  DIV_REG, DIV_IMM,
  AND_REG, AND_IMM,
  OR_REG,  OR_IMM,

  CMP_REG, CMP_IMM,

  INC, DEC,

  // Stack operations 
  PUSH_REG, PUSH_IMM, POP,
  CALL, RET,

  JMP,
  JG,JGE, JE,
  JA,JAE,

  HLT
}Inst;

typedef enum {
  /** General Purpose */
  R1 = 0x00, R2, R3,
  R4, R5, R6,
  R7, R8, 
  
  /** Machine based register */
  PC, SP, FP
}Reg;



#endif