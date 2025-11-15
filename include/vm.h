#ifndef VM_H
#define VM_H

#define MAX 65535
#define MAX_REG 8

#include <stdint.h>
#include <stdlib.h>
#include "memory.h"
#include <assert.h>

typedef uint16_t    Word;
typedef uint8_t     Byte;
typedef uint32_t    u32;

typedef struct {
    Word regs[MAX_REG];
    Byte mem[MAX];
    bool cf, of, zf, sf;
    Word pc;
    Word sp;
    Word fp;

    bool halted;
}Vm;


inline void vm_init(Vm* vm) {
    vm->cf = vm->sf = vm->of = vm->zf = false;
    vm->pc = 0;
    vm->sp = 0xFFFE;
    vm->fp = 0xFFFE;

    vm->halted = false;
    for (int i = 0;i < MAX_REG; i++) vm->regs[i] = 0;
    for (int i = 0;i < MAX; i++) vm->mem[i] = 0;
}

void vm_load_program(Vm* vm, Byte* program, Word len){
    Byte* mem = vm->mem;
    for (int i =0;i < len;i++) {
        mem[i] = program[i];
    }
}

inline Word vm_fetch16(Vm* vm) {
    Byte low = vm->mem[vm->pc++];
    Byte high = vm->mem[vm->pc++];
    return (Word)((high << 8) | low);
} 

inline Word vm_getRegister(Vm* vm, Reg reg) {
    if (reg >= MAX_REG) {
        switch (reg) {
            case SP: return vm->sp;
            case FP: return vm->fp;
            case PC: return vm->pc;
            default:
                printf("Error register out of bound %d\n", reg);
                return 0;
        }
    }
    return vm->regs[reg];
}


inline void vm_setregister(Vm* vm, Reg reg, Word value) {
    if (reg >= R1 && reg <= R8)
        vm->regs[reg] = value;
    else if (reg == PC)
        vm->pc = value;
    else if (reg == SP)
        vm->sp = value;
    else if (reg == FP)
        vm->fp = value;
    else {
        printf("Invalid register index %d\n", reg);
        exit(1);
    }
}


inline void vm_store16(Vm* vm, Word address, Word value) {
    vm->mem[address] = value & 0xFF;
    vm->mem[address + 1] = (value >> 8) & 0xFF; 
}

inline Byte vm_fetch8(Vm* vm) {
    return vm->mem[vm->pc++];
}


/**
    Stack semantics in here 
    sp = 0xfffe     
    
 */

void vm_push(Vm* vm, Word value) {
    vm->sp-=2;
    vm->mem[vm->sp] = value & 0xFF;
    vm->mem[vm->sp + 1] = (value >> 8) & 0xFF; 
}


Word vm_pop(Vm *vm) {
    Word value = vm->mem[vm->sp] | (vm->mem[vm->sp + 1] << 8);
    vm->sp += 2;
    return value;
}

void vm_step(Vm* vm) {
    Inst opcode = vm_fetch8(vm);
    
    switch(opcode){
        case MOV_REG: {
            Reg r1 = vm_fetch8(vm);
            Reg r2 = vm_fetch8(vm);
            Word value = vm_getRegister(vm, r2);
            vm_setregister(vm, r1, value);
        }break;
        case MOV_IMM: {
            Reg r1 = vm_fetch8(vm);
            Word imm = vm_fetch16(vm);
            vm_setregister(vm, r1, imm);
        }break;
        case LOAD: {
            Byte r1 = vm_fetch8(vm);
            Byte r2 = vm_fetch8(vm);
            Word offset = vm_fetch16(vm);
            Word addr = vm_getRegister(vm, r2) + offset;
            if (addr >= MAX) {printf("Invalid memory access"); break;}
            vm_setregister(vm, r1, (vm->mem[addr]) | (vm->mem[addr + 1] << 8)); 
        }break;
        case STORE: {
            Byte r1 = vm_fetch8(vm);
            Word offset = vm_fetch16(vm);
            Byte src = vm_fetch8(vm);
            Word addr = vm_getRegister(vm, r1) + offset;
            if (addr >= MAX) {printf("Invalid memory access"); break;}
            vm_store16(vm, addr, vm_getRegister(vm, src));
        }break;
        case ADD_IMM: {
            Reg r1  = vm_fetch8(vm); 
            Word imm = vm_fetch16(vm);
            Word value = vm_getRegister(vm,r1);
            u32 res = (u32)value + (u32)imm;
            Word result = (Word)res;
            vm_setregister(vm,r1,result); 
            
            vm->cf = (res > MAX);
            vm->zf = (res == 0);
            vm->sf = (res >> 15) & 1;

            bool sign_a = (value >> 15) & 1;
            bool sign_b = (imm >> 15) & 1;
            bool sign_r = (result >> 15) & 1;
            vm->of = ((sign_a == sign_b) && (sign_a != sign_r));         
        }break;
        case ADD_REG: {
            Reg r1 = vm_fetch8(vm);
            Reg r2 = vm_fetch8(vm);
            Word v1 = vm_getRegister(vm,r1);
            Word v2 = vm_getRegister(vm,r2);

            u32 res = (u32)v1 + (u32)v2;
            Word result = (Word)res;
            
            vm_setregister(vm, r1, result);

            vm->cf = (res >> 16) & 1;
            vm->zf = (res == 0);
            vm->sf = (res >> 15) & 1;

            bool sign_a = (v1 >> 15) & 1; // (+)
            bool sign_b = (v2 >> 15) & 1; // (+)
            bool sign_r = (result >> 15) & 1; // (+)
            vm->of = ((sign_a == sign_b) && (sign_a != sign_r)); 
        }break;
        case MUL_IMM: {
            Reg r1 = vm_fetch8(vm);
            Word value = vm_getRegister(vm,r1);
            Word imm = vm_fetch16(vm);  

            u32 res = (u32)value * (u32)imm;
            Word result = (Word)res;

            vm_setregister(vm,r1,result);

            vm->cf = (res >> 16) & 1;
            vm->zf = (res == 0);
            vm->sf = (res >> 15) & 1;    
            vm->cf = vm->of = ((res >> 16) != 0);
        }break;
        case MUL_REG: { 
            Reg r1 = vm_fetch8(vm);
            Reg r2 = vm_fetch8(vm);
            Word v1 = vm_getRegister(vm, r1);
            Word v2 = vm_getRegister(vm, r2);

            u32 res = (u32)v1 * (u32)v2;
            Word result = (Word)res;

            vm_setregister(vm,r1, result);

            vm->cf = (res >> 16) & 1;
            vm->zf = (res == 0);
            vm->sf = (res >> 15) & 1;    
            vm->cf = vm->of = ((res >> 16) != 0);
        }break;
        case JMP: {
            Word address = vm_fetch16(vm);
            vm->pc = address;
        }break;
        case CMP_REG: {
            Byte r1 = vm_fetch8(vm); 
            Byte r2 = vm_fetch8(vm);
            Word v1 = vm_getRegister(vm, r1);
            Word v2 = vm_getRegister(vm, r2);

            u32 res = (u32)v1 - (u32)v2;
            Word result = (Word)res;
            vm->cf = (v1 < v2);
            vm->zf = (res == 0);
            vm->sf = (res >> 15) & 1;

            bool sign_a = (v1 >> 15) & 1; 
            bool sign_b = (v2 >> 15) & 1; 
            bool sign_r = (result >> 15) & 1; 
            // vm->of = ((sign_a == sign_b) && (sign_a != sign_r));
            vm->of = ((sign_a != sign_b) && (sign_r == sign_b));
        }break;
        case CMP_IMM: {
            Byte r1 = vm_fetch8(vm);
            Word imm = vm_fetch16(vm);

            Word v1 = vm_getRegister(vm, r1);
            Word v2 = imm;

            u32 res = (u32)v1 - (u32)v2;
            Word result = (Word)res;

            vm->cf = (v1 < v2);
            vm->zf = (result == 0);
            vm->sf = (result >> 15) & 1;

            bool sign_a = (v1 >> 15) & 1;
            bool sign_b = (v2 >> 15) & 1;
            bool sign_r = (result >> 15) & 1;

            vm->of = ((sign_a != sign_b) && (sign_r == sign_b));
        } break;
        case JG: {
            Word address = vm_fetch16(vm);
            if (!vm->zf && (vm->sf == vm->of))  {
                vm->pc = address;
            } 
        }break;
        case JA: { 
            Word address = vm_fetch16(vm);
            if (!vm->cf && !vm->zf) {
                vm->pc = address;
            }
        } break;
        case AND_IMM: {
            Reg r1 = vm_fetch8(vm);
            Word v1 = vm_getRegister(vm, r1);
            Word v2 = vm_fetch16(vm);

            Word result = v1 & v2;
            vm_setregister(vm, r1, result);
            vm->cf = 0;
            vm->of = 0;
            vm->sf = (result >> 15) & 1;
            vm->zf = (result == 0);
        }break; 
        case AND_REG: {
            Reg r1 = vm_fetch8(vm);
            Reg r2 = vm_fetch8(vm);
            Word v1 = vm_getRegister(vm, r1);
            Word v2 = vm_getRegister(vm, r2);
           
            Word result = v1 & v2;

            vm_setregister(vm, r1, result);
            vm->of = 0;
            vm->cf = 0;
            vm->zf = (result == 0);
            vm->sf = (result >> 15) & 1;
        }break;
        case JGE: {
            Word address = vm_fetch16(vm);
            if (vm->sf == vm->of) {
                vm->pc = address;
            }
        }break;
        case JAE: {
            Word address = vm_fetch16(vm);
            if (!vm->cf) {
                vm->pc = address;
            }
        }break;
        case JE: {
            Word address = vm_fetch16(vm);
            if (vm->zf) {
                vm->pc = address;
            }
        }break;
        case INC: {
            Reg r1 = vm_fetch8(vm);
            Word value = vm_getRegister(vm,r1);
            value++;
            vm_setregister(vm, r1, value);
            vm->of = (value == 0x7FFF);
            vm->zf = (value == 0);
            vm->sf = (value >> 15) & 1;
        }break;
        case DEC: {
            Reg r1 = vm_fetch8(vm);
            Word value = vm_getRegister(vm, r1);
            value--;
            vm_setregister(vm, r1, value);
            vm->of = (value == 0x8000);
        }break;
        case PUSH_IMM: {
            Word value = vm_fetch16(vm);
            vm_push(vm, value);
        }break;
        case PUSH_REG: {
            Reg r1 = vm_fetch8(vm);
            Word value = vm_getRegister(vm, r1);
            vm_push(vm, value);
        }break;
        case POP: {
            Reg r1 = vm_fetch8(vm);
            Word value = vm_pop(vm);
            vm_setregister(vm, r1, value);
        }break;
        case CALL: {
            Word address = vm_fetch16(vm);
            Word return_addr = vm->pc;
            vm_push(vm, return_addr);
            vm->pc = address;
        }break;
        case RET: {
            Word address = vm_pop(vm);
            vm->pc = address;
        }break; 
        case HLT: {
            vm->halted = true;
            return;
        }break;
        default:
        printf("Unknown Instruction %d %d \n",vm->pc, opcode);
        break;
    }    
}

void vm_dump_bytecode(Vm* vm, const char* filename, size_t size) {
    FILE* f = fopen(filename, "wb");
    if (!f) {
        perror("Error opening dump file");
        return;
    }

    size_t written = fwrite(vm->mem, 1, size, f);
    fclose(f);

    if (written != size) {
        fprintf(stderr, "⚠️  Warning: wrote only %zu of %zu bytes\n", written, size);
    } else {
        printf("✅ Dumped %zu bytes from VM memory to '%s'\n", size, filename);
    }
}

size_t vm_load_bytecode_from_file(Vm* vm, const char* filename) {
    FILE* f = fopen(filename, "rb");
    if (!f) {
        perror("Error opening file for loading");
        return -1;
    }

    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (file_size <= 0) {
        fprintf(stderr, "⚠️  File '%s' is empty or invalid\n", filename);
        fclose(f);
        return -1;
    }

    if (file_size > (long)sizeof(vm->mem)) {
        fprintf(stderr, "⚠️  File too large (%ld bytes), truncating to %zu\n", file_size, sizeof(vm->mem));
        file_size = sizeof(vm->mem);
    }

    size_t read = fread(vm->mem, 1, file_size, f);
    fclose(f);

    if (read != (size_t)file_size) {
        fprintf(stderr, "⚠️  Warning: read only %zu of %ld bytes\n", read, file_size);
    }

    return read;
}

void vm_execute(Vm *vm) {
    while (!vm->halted) {
        vm_step(vm);
    }
}


void debug_stack(Vm* vm, int count) {
    printf("Stack (top -> bottom):\n");
    Word sp = vm->sp;

    for (int i = 0; i < count; i++) {
        if (sp + i*2 + 1 >= 0x10000) break; // prevent overflow
        Word value = vm->mem[sp + i*2] | (vm->mem[sp + i*2 + 1] << 8); // little-endian
        printf("0x%04X: 0x%04X\n", sp + i*2, value);
    }
}


/* DEBUG */
void print_internal(Vm* vm) {
    printf("Flags Debug carry %d\n", vm->cf);
    printf("Flags Debug sign %d\n", vm->sf);
    printf("Flags Debug overflow %d\n", vm->of);
    printf("Flags Debug zero %d\n", vm->zf);

    printf("---------------------------------\n");
    printf("Reg Debug \n");
    for (int i = 0;i < MAX_REG;i++) printf("%d ",(uint16_t)vm->regs[i]);
    printf("\n");

    printf("PC, SP, FP %d %d %d\n",vm->pc, vm->sp, vm->fp);
    // printf("Memory Dump (first 256 words)\n");
    // for (int row = 0; row < 16; row++) {
    //     printf("%04X: ", row * 16);
    //     for (int col = 0; col < 16; col++) {
    //         printf("%04X ", vm->mem[row * 16 + col]);
    //     }
    //     printf("\n");
    // }

    printf("Stack debug \n");
    for (int i = 0XFFFE;i > 0XFFFE - 15; i--) {
        printf("%04X ", vm->mem[i]);
    }
    printf("\n");
    printf("%4X %04X\n",vm->fp, vm->sp);
}

#endif