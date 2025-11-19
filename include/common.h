#ifndef COMMON_H
#define COMMON_H

#include <stdint.h>


typedef uint16_t   Word;
typedef uint8_t    Byte;
typedef uint32_t   u32;

#define MAX        65535
#define MAX_REG    8

#define MMIO_START      0xFF00
#define MMIO_END        0xFFFF

#define IO_IN           0xFF00
#define IO_OUT          0xFF01

#define vm_fetch_label(vm) \
    Word entry = vm->mem[0] | (vm->mem[1] << 8);\
    vm->pc = entry;


#endif
