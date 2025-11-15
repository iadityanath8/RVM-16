# ==============================
# rvm-16 Makefile (Simple: src → bin)
# ==============================

CC      := gcc
CFLAGS  := -Wall -Wextra  -Iinclude -O3
LDFLAGS :=

SRC_DIR   := src
INC_DIR   := include
BIN_DIR   := bin
TARGET    := $(BIN_DIR)/vm

# All .c files in src/
SRCS := $(wildcard $(SRC_DIR)/*.c)
# Object files in same folder (no build/)
OBJS := $(SRCS:.c=.o)

.PHONY: all clean run

# Build target
all: $(TARGET)

# Link object files → bin/vm
$(TARGET): $(OBJS) | $(BIN_DIR)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

# Compile .c → .o (in src/)
$(SRC_DIR)/%.o: $(SRC_DIR)/%.c | $(BIN_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Create bin/ if missing
$(BIN_DIR):
	mkdir -p $@

# Clean: delete .o and bin/
clean:
	rm -f $(SRC_DIR)/*.o
	rm -rf $(BIN_DIR)

start:
    mov r1, 2
    mov r2, 3
    call add_fn 

    hlt

add_fn:   
    push fp
    mov fp, sp 
    push 20
    add r1, r2 
    pop r3 
    add r1, r3    
    pop fp 
    ret
# Run: build + execute
run: all
	./$(TARGET) examples/hello.bin

# Optional: force rebuild
rebuild: clean all
