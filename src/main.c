#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "../include/instructions.h"
#include "../include/vm.h"


int maiwwn() {
    Byte Program[] = {
        0x2,0x0,
        MOV_IMM,R1,0x4,0x0,
        DIV_IMM,R1,0x2,0x0,
        HLT,
    };    

    Vm vm;
    vm_init(&vm);
    
    Word prog_size = sizeof(Program) / sizeof(Program[0]);
    vm_load_program(&vm,Program,prog_size);
    
    vm_execute(&vm);
    

    print_internal(&vm);
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
        
        printf("✅ Loaded %zu bytes from '%s'\n", size, filename);
        printf("▶ Running program...\n");
        
        vm_execute(&vm);
        printf("✅ Program finished.\n");
        print_internal(&vm);
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