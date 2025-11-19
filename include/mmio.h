#ifndef MMIO_H
#define MMIO_H

#include <stdbool.h>
#include <stdio.h>
#include "common.h"


typedef struct Vm Vm;

static inline bool is_mmio_address(uint16_t address) {  
    return address >= MMIO_START && address <= MMIO_END;
}


static inline uint8_t mmio_read(Vm* vm, Word address) {
    switch(address) {
        case IO_IN: {
            int c = getchar();
            return (c == EOF) ? 0: (Byte)c;
        }break;
        default: 
            return 0;
    }
} 

static inline void mmio_write(Vm* vm, Word address, Byte value) {
    switch(address) {
        case IO_OUT: {
            putchar(value);
            fflush(stdout);
        }break;
        default: 
            break;
    }
}

#endif 



