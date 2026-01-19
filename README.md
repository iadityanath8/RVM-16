# 🖥️RVM-16 Custom 16-bit Virtual Machine & Assembler

A lightweight, educational 16-bit virtual machine with a custom instruction set and Python-based assembler. Features include arithmetic operations, memory addressing, stack management, function calls, and memory-mapped I/O.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Instruction Set](#instruction-set)
- [Assembly Language Syntax](#assembly-language-syntax)
- [Examples](#examples)
- [Memory Layout](#memory-layout)
- [Function Calling Convention](#function-calling-convention)
- [Contributing](#contributing)

## ✨ Features

- **16-bit architecture** with word-addressable memory
- **Custom instruction set** with 30+ instructions
- **Python assembler** that compiles assembly to bytecode
- **Stack-based function calls** with frame pointer support
- **Memory-mapped I/O** for output operations
- **Arithmetic operations** with flag support (ZF, SF, CF, OF)
- **Conditional jumps** for control flow
- **Label-based addressing** for easy programming

## 🏗️ Architecture

### Registers

| Register | Purpose | Size |
|----------|---------|------|
| `r0-r7` | General purpose | 16-bit |
| `sp` | Stack pointer | 16-bit |
| `fp` | Frame pointer | 16-bit |
| `pc` | Program counter | 16-bit |

### Flags

- **ZF** (Zero Flag): Set when result is zero
- **SF** (Sign Flag): Set when result is negative (MSB = 1)
- **CF** (Carry Flag): Set on unsigned overflow/underflow
- **OF** (Overflow Flag): Set on signed overflow

### Memory

- **Address space**: 64KB (0x0000 - 0xFFFF)
- **Word size**: 16 bits (2 bytes)
- **Endianness**: Little-endian
- **I/O Port**: `0xFFFE` (character output)

## 📦 Installation

### Prerequisites

- Python 3.10+
- GCC or Clang (for VM compilation)

### Build the VM

```bash
# Clone the repository
git clone https://github.com/iadityanath8/rvm-16.git
cd custom-vm

# Compile the VM
gcc -o rvm vm.c -Wall -Wextra

# Or with optimizations
gcc -o rvm vm.c -O3 -Wall -Wextra
```

### Install Python dependencies

```bash
pip install -r requirements.txt  # If any dependencies exist
```

## 🚀 Quick Start

### 1. Write Assembly Code

Create a file `hello.ras`:

```nasm
.entry main

OUTPUT_PORT = 0xFFFE

main:
    mov r0, OUTPUT_PORT
    
    store [r0], 72      ; 'H'
    store [r0], 101     ; 'e'
    store [r0], 108     ; 'l'
    store [r0], 108     ; 'l'
    store [r0], 111     ; 'o'
    store [r0], 10      ; '\n'
    
    hlt
```

### 2. Assemble to Bytecode

```bash
python assembler.py hello.ras -o hello.rvm
```

### 3. Run on VM

```bash
./rvm hello.rvm
```

Output:
```
Hello
```

## 📚 Instruction Set

### Data Movement

| Instruction | Syntax | Description |
|-------------|--------|-------------|
| `mov` | `mov r1, r2` / `mov r1, imm` | Move value to register |
| `load` | `load r1, [r2 + offset]` | Load from memory |
| `store` | `store [r1 + offset], r2` | Store register to memory |
| `store` | `store [r1 + offset], imm` | Store immediate to memory |

### Arithmetic

| Instruction | Syntax | Description |
|-------------|--------|-------------|
| `add` | `add r1, r2` / `add r1, imm` | Addition |
| `sub` | `sub r1, r2` / `sub r1, imm` | Subtraction |
| `mul` | `mul r1, r2` / `mul r1, imm` | Multiplication |
| `div` | `div r1, r2` / `div r1, imm` | Division |
| `inc` | `inc r1` | Increment |
| `dec` | `dec r1` | Decrement |

### Logical

| Instruction | Syntax | Description |
|-------------|--------|-------------|
| `and` | `and r1, r2` / `and r1, imm` | Bitwise AND |
| `or` | `or r1, r2` / `or r1, imm` | Bitwise OR |
| `cmp` | `cmp r1, r2` / `cmp r1, imm` | Compare (sets flags) |

### Control Flow

| Instruction | Syntax | Description |
|-------------|--------|-------------|
| `jmp` | `jmp label` | Unconditional jump |
| `je` | `je label` | Jump if equal (ZF = 1) |
| `jg` | `jg label` | Jump if greater (signed) |
| `jge` | `jge label` | Jump if greater or equal |
| `ja` | `ja label` | Jump if above (unsigned) |
| `jae` | `jae label` | Jump if above or equal |

### Stack Operations

| Instruction | Syntax | Description |
|-------------|--------|-------------|
| `push` | `push r1` / `push imm` | Push to stack |
| `pop` | `pop r1` | Pop from stack |
| `call` | `call label` | Call function |
| `ret` | `ret` | Return from function |

### System

| Instruction | Syntax | Description |
|-------------|--------|-------------|
| `hlt` | `hlt` | Halt execution |

## 📝 Assembly Language Syntax

### Comments

```nasm
; This is a single-line comment
# This is also a comment
```

### Labels

```nasm
main:           ; Label on its own line
    mov r0, 10

loop: inc r0    ; Label with instruction on same line
```

### Entry Point

```nasm
.entry main     ; Set program entry point
```

### Constants

```nasm
BUFFER_SIZE = 256
OUTPUT_PORT = 0xFFFE

mov r0, BUFFER_SIZE     ; Use constant
```

### Memory Addressing

```nasm
; Direct register
load r0, [r1]           ; Load from address in r1

; Register + offset
load r0, [r1 + 100]     ; Load from r1 + 100
store [r2 - 50], r3     ; Store to r2 - 50

; Frame pointer relative (for local variables)
load r0, [fp - 2]       ; Load local variable
store [fp + 4], r1      ; Access function argument
```

### Number Formats

```nasm
mov r0, 42              ; Decimal
mov r0, 0xFF            ; Hexadecimal
mov r0, 0x1000          ; Hexadecimal
```

## 💡 Examples

### Example 1: Simple Addition

```nasm
.entry main

main:
    mov r0, 10
    mov r1, 20
    add r0, r1          ; r0 = 30
    hlt
```

### Example 2: Loop

```nasm
.entry main

main:
    mov r0, 0           ; Counter
    mov r1, 10          ; Limit

loop:
    inc r0
    cmp r0, r1
    jg done             ; Jump if r0 > r1
    jmp loop

done:
    hlt
```

### Example 3: Function Call

```nasm
.entry main

add_numbers:
    push fp
    mov fp, sp
    
    load r0, [fp + 4]   ; arg1
    load r1, [fp + 6]   ; arg2
    add r0, r1          ; r0 = result
    
    pop fp
    ret

main:
    push 15
    push 25
    call add_numbers
    add sp, 4           ; Clean up arguments
    
    ; Result in r0 = 40
    hlt
```

### Example 4: Local Variables

```nasm
.entry main

calculate:
    push fp
    mov fp, sp
    sub sp, 4           ; Allocate 2 local variables
    
    ; Store locals
    store [fp - 2], 100  ; local1 = 100
    store [fp - 4], 200  ; local2 = 200
    
    ; Use locals
    load r0, [fp - 2]
    load r1, [fp - 4]
    add r0, r1
    
    mov sp, fp          ; Clean up
    pop fp
    ret

main:
    call calculate
    hlt
```

### Example 5: Print String

```nasm
.entry main

OUTPUT_PORT = 0xFFFE

msg: .db 72, 101, 108, 108, 111, 0  ; "Hello\0"

print_string:
    push fp
    mov fp, sp
    
    load r0, [fp + 4]       ; Get string address
    mov r2, OUTPUT_PORT
    
print_loop:
    load r1, [r0]           ; Load character
    cmp r1, 0               ; Check null terminator
    je print_done
    
    store [r2], r1          ; Print character
    inc r0                  ; Next character
    jmp print_loop

print_done:
    pop fp
    ret

main:
    push msg
    call print_string
    add sp, 2
    hlt
```

## 🗺️ Memory Layout

```
0x0000  ┌─────────────────┐
        │  Entry Point    │  2 bytes (program start address)
0x0002  ├─────────────────┤
        │                 │
        │  Program Code   │
        │                 │
        ├─────────────────┤
        │                 │
        │  Data / Heap    │
        │                 │
        ├─────────────────┤
        │       ↓         │
        │    (grows)      │
        │                 │
        │       ↑         │
        │    Stack        │
0xFFFC  ├─────────────────┤
0xFFFD  │  OUTPUT_FLUSH   │  Buffer flush port
0xFFFE  │  OUTPUT_PORT    │  Character output port
0xFFFF  └─────────────────┘
```

## 🔧 Function Calling Convention

### Stack Frame Layout

```
Higher addresses
    ┌─────────────────┐
    │  arg2           │  [fp + 6]
    ├─────────────────┤
    │  arg1           │  [fp + 4]
    ├─────────────────┤
    │  return address │  [fp + 2]  (pushed by CALL)
    ├─────────────────┤
FP→ │  saved FP       │  [fp]      (pushed by callee)
    ├─────────────────┤
    │  local1         │  [fp - 2]
    ├─────────────────┤
    │  local2         │  [fp - 4]
    ├─────────────────┤
SP→ │  ...            │
    └─────────────────┘
Lower addresses
```

### Calling Convention Rules

1. **Caller**:
   - Push arguments in reverse order (right to left)
   - Call function with `call label`
   - Clean up arguments after return: `add sp, N` (N = num_args × 2)
   - Result is in `r0`

2. **Callee**:
   - Save frame pointer: `push fp`
   - Set new frame pointer: `mov fp, sp`
   - Allocate locals: `sub sp, N`
   - Restore frame pointer: `pop fp` before `ret`
   - **Never push extra data without balancing pops before ret!**

### Example

```nasm
; Caller
push 10             ; arg1
push 20             ; arg2
call my_function
add sp, 4           ; Clean up 2 arguments (2 words = 4 bytes)

; Callee
my_function:
    push fp         ; Save old FP
    mov fp, sp      ; Set new FP
    sub sp, 2       ; Allocate 1 local variable
    
    load r0, [fp + 4]   ; Access arg1
    load r1, [fp + 6]   ; Access arg2
    store [fp - 2], r0  ; Use local variable
    
    ; ... function body ...
    
    mov sp, fp      ; Clean up locals
    pop fp          ; Restore old FP
    ret             ; Return (pops return address)
```

## 🎯 Memory-Mapped I/O

### Character Output

Write to address `0xFFFE` to print a character:

```nasm
OUTPUT_PORT = 0xFFFE

mov r0, OUTPUT_PORT
store [r0], 65      ; Prints 'A'
```

### Buffered I/O (Optional)

If implemented with buffering:

```nasm
OUTPUT_PORT = 0xFFFE
OUTPUT_FLUSH = 0xFFFD

mov r0, OUTPUT_PORT
store [r0], 72      ; Buffer 'H'
store [r0], 105     ; Buffer 'i'

mov r1, OUTPUT_FLUSH
store [r1], 0       ; Flush buffer, prints "Hi"
```

## 🐛 Common Pitfalls

### 1. ❌ Pushing inside function without proper cleanup

```nasm
my_function:
    push r1         ; ❌ WRONG! Corrupts stack for ret
    ret             ; Will jump to wrong address!
```

✅ **Correct**:
```nasm
my_function:
    push fp
    mov fp, sp
    sub sp, 2           ; Allocate space
    store [fp - 2], r1  ; Save r1 to local
    
    ; ... use r1 ...
    
    load r1, [fp - 2]   ; Restore r1
    mov sp, fp
    pop fp
    ret
```

### 2. ❌ Forgetting to clean up arguments

```nasm
push 10
push 20
call my_function
; ❌ Stack still has arguments!
hlt
```

✅ **Correct**:
```nasm
push 10
push 20
call my_function
add sp, 4           ; Clean up 2 words (4 bytes)
hlt
```

### 3. ❌ Using wrong offsets for arguments

```nasm
my_function:
    push fp
    mov fp, sp
    load r0, [fp + 2]   ; ❌ This is return address!
```

✅ **Correct**:
```nasm
my_function:
    push fp
    mov fp, sp
    load r0, [fp + 4]   ; ✅ First argument
    load r1, [fp + 6]   ; ✅ Second argument
```

## 📖 Assembler Usage

### Command Line

```bash
# Basic usage
python assembler.py input.ras

# Specify output file
python assembler.py input.ras -o output.rvm

# Show debug information
python assembler.py input.ras --debug
```

### Programmatic Usage

```python
from assembler import Assembler

# Read assembly file
with open("program.ras", "r") as f:
    content = f.readlines()

# Assemble
assembler = Assembler(content)
bytecode = assembler.assemble()

# Write bytecode
with open("program.rvm", "wb") as f:
    f.write(bytecode)

# Print labels (for debugging)
print("Labels:", assembler.labels)
print("Entry point:", assembler.entry_point)
```

## 🔬 VM Usage

### Running Programs

```bash
./vm program.rvm
```

### VM Implementation

The VM is implemented in C with the following features:

- Instruction decoder with switch-case dispatch
- 16-bit register file
- 64KB addressable memory
- Stack implementation (grows downward)
- Flag register for conditional operations
- Memory-mapped I/O for output

## 🤝 Contributing

Contributions are welcome! Here are some areas for improvement:

- [ ] Add more instructions (shift, rotate, xor, not)
- [ ] Implement interrupts
- [ ] Add debugging support (breakpoints, stepping)
- [ ] Create standard library functions
- [ ] Optimize VM performance
- [ ] Add more I/O capabilities
- [ ] Implement file I/O
- [ ] Add floating-point support

### How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by classic 16-bit architectures (8086, PDP-11)
- Educational resource for learning VM design and implementation
- Built as a learning project for understanding low-level programming

## 📞 Contact

- GitHub: [@iadityanath8](https://github.com/iadityanath8)
- Email: iadityanath8@gmail.com

---

**Made with ❤️ for learning and education**
