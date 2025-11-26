#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "../include/instructions.h"
#include "../include/vm.h"

//#define IO_IN           0xFF00
// [0x00] [0xff]
// 0 - 255 
// little endian  16 65535 2**64 

int mai2n() {
    Byte Program[] = {
        0x02,0x00, //
        MOV_IMM, R1, 0x00, 0xFF,   // R1 = 0xFF00 (IO_IN)
        LOAD, R2, R1, 0x00, 0x00,  // R2 = [R1 + 0x00] -> reads one char

        MOV_IMM, R1, 0x01, 0xFF,
        STORE_REG, R1, 0x00, 0x00, R2,
        // MOV_IMM, R1, 0x01, 0xFF,   // R1 = 0xFF00 (IO_OUT)
        // STORE_REG, R1, 0x00, R2,   // prints char
        HLT
    };


    Vm vm;
    vm_init(&vm);
    
    Word prog_size = sizeof(Program) / sizeof(Program[0]);
    vm_load_program(&vm,Program,prog_size);

    
    vm_execute(&vm);
    
    return 0;
}

int main(int argc, char* argv[]) {
    Vm vm;
    vm_init(&vm);
    
    if (argc < 2) {
        printf("Usage:\n");
        printf("  vm -load <file>        Load and execute bytecode\n");
        printf("  vm -dump <file> <size> Dump current VM memory to file\n");
        printf("  vm -info               Show registers/state\n");
        printf("\nExample:\n  vm -load program.bin\n");
        return 0;
    }

    if (strcmp(argv[1], "-load") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Error: Missing filename.\n");
            return 1;
        }
        const char* filename = argv[2];
        size_t size = vm_load_bytecode_from_file(&vm, filename);
        
        // printf("✅ Loaded %zu bytes from '%s'\n", size, filename);
        // printf("▶ Running program...\n");
        
        vm_execute(&vm);
        // printf("memory address at 21 is %d\n", vm.mem[21]);
        // printf("✅ Program finished.\n");
        // print_internal(&vm);
    }

    else if (strcmp(argv[1], "-dump") == 0) {
        if (argc < 4) {
            fprintf(stderr, "Error: Missing filename or size.\n");
            return 1;
        }
        const char* filename = argv[2];
        size_t size = (size_t)atoi(argv[3]);
        vm_dump_bytecode(&vm, filename, size);
    }

    else if (strcmp(argv[1], "-info") == 0) {
        print_internal(&vm);
    }

    else {
        fprintf(stderr, "Unknown command: %s\n", argv[1]);
    }

    return 0;
}
