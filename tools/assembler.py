from instructions import Inst, Reg
import re

INST_TABLE = {
    'mov': {'reg': Inst.MOV_REG, 'imm': Inst.MOV_IMM, 'argc': 2},
    'load': {'opcode': Inst.LOAD, 'argc': 2},
    'store': {'reg': Inst.STORE_REG, 'imm': Inst.STORE_IMM, 'argc': 2},
    'add': {'reg': Inst.ADD_REG, 'imm': Inst.ADD_IMM, 'argc': 2},
    'sub': {'reg': Inst.SUB_REG, 'imm': Inst.SUB_IMM, 'argc': 2},
    'mul': {'reg': Inst.MUL_REG, 'imm': Inst.MUL_IMM, 'argc': 2},
    'div': {'reg': Inst.DIV_REG, 'imm': Inst.DIV_IMM, 'argc': 2},

    'and': {'reg': Inst.AND_REG, 'imm': Inst.AND_IMM, 'argc': 2},
    'or':  {'reg': Inst.OR_REG,  'imm': Inst.OR_IMM,  'argc': 2},

    'cmp': {'reg': Inst.CMP_REG, 'imm': Inst.CMP_IMM, 'argc': 2},

    'inc': {'opcode': Inst.INC, 'argc': 1},
    'dec': {'opcode': Inst.DEC, 'argc': 1},

    'push': {'reg': Inst.PUSH_REG, 'imm': Inst.PUSH_IMM, 'argc': 1},
    'pop':  {'opcode': Inst.POP, 'argc': 1},

    'call': {'opcode': Inst.CALL, 'argc': 1},
    'ret':  {'opcode': Inst.RET, 'argc': 0},

    'jmp': {'opcode': Inst.JMP, 'argc': 1},
    'jg':  {'opcode': Inst.JG,  'argc': 1},
    'jge': {'opcode': Inst.JGE, 'argc': 1},
    'je':  {'opcode': Inst.JE,  'argc': 1},
    'ja':  {'opcode': Inst.JA,  'argc': 1},
    'jae': {'opcode': Inst.JAE, 'argc': 1},

    'hlt': {'opcode': Inst.HLT, 'argc': 0},
}

REG_TABLE = {r.name.lower(): r for r in Reg}

def expect_arg(inst,num:int):
    if INST_TABLE[inst]['argc'] == num:
        return True
    else:
        return False
    

def u16(n: int) -> list[int]:
    return [n & 0xFF, (n >> 8) & 0xFF]

def as_list(x):
    return [x] if isinstance(x, int) else x


class Assembler:
    def __init__(self, content: str):
        self.cleaned = [line for line in content if line.strip() != ""]
        self.labels = {}
        self.program  = bytearray()
        self.entry_label = None 
        self.entry_point = None 

    def get_reg(self,name: str) -> Reg:
        key = name.lower()
        if key not in REG_TABLE:
            raise ValueError(f"Unknown register: {name}")
        return REG_TABLE[key]
    
    def get_opcode(self, name: str, args: list):
        name = name.lower()
        
        if name not in INST_TABLE:
            raise ValueError(f"Unknown instruction: {name}")

        entry = INST_TABLE[name]
        argc = entry["argc"]

        if len(args) - 1 != argc:
            raise ValueError(f"{name} expects {argc} arguments.")

        if "opcode" in entry:
            return entry["opcode"]

        operand = args[-1]

        if operand.lower().startswith('r') or operand in ('fp', 'sp', 'pc'):
            return entry["reg"]
        else:
            return entry["imm"]

    def get_reg_imm(self,cs:str) -> int: 
        cs = cs.lower().strip()

        if cs in REG_TABLE:
            return REG_TABLE[cs].value
        
        if cs.isnumeric():
            return u16(int(cs))
        
        elif cs.startswith('0x'):
            return u16(int(cs, 16))
        
        raise ValueError(f"Invalid operand: {cs}")

    def pass_label(self, lines):
        pc = 0
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith(";") or line.startswith("#"):
                continue
            
            if line.startswith(".entry"):
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError(".entry must be followed by a label name")
                self.entry_label = parts[1].strip()
                continue
            
            if ":" in line:
                colon_pos = line.find(":")
                label_name = line[:colon_pos].strip()
                self.labels[label_name] = pc
                
                after_label = line[colon_pos + 1:].strip()
                if not after_label or after_label.startswith(";") or after_label.startswith("#"):
                    continue  
                
                line = after_label
            
            parts = line.replace(",", " ").split()
            if not parts:
                continue
            
            inst = parts[0].lower()
            
            if inst not in INST_TABLE:
                continue     
            
            entry = INST_TABLE[inst]
            
            if inst == 'load':
                pc += 5  
                continue
            
            if inst == 'store':
                bracket_end = line.find(']')
                if bracket_end == -1:
                    raise ValueError("STORE instruction missing closing bracket")
                
                after_bracket = line[bracket_end + 1:].strip()
                if after_bracket.startswith(','):
                    after_bracket = after_bracket[1:].strip()
                
                value_str = after_bracket.split()[0].strip().lower()
                
                if value_str in REG_TABLE or value_str in ('sp', 'fp', 'pc'):
                    pc += 4  
                else:
                    pc += 5  
                continue
            
            argc = entry["argc"]
            pc += 1  # opcode byte
            
            if argc == 0:
                continue
            
            if argc == 1:
                arg = parts[1].lower()
                # Check if it's a label (will be resolved as 16-bit address)
                if arg in self.labels:
                    pc += 2
                # Check if it's a register (8-bit)
                elif arg.startswith("r") or arg in ("sp", "fp", "pc"):
                    pc += 1
                # Otherwise it's an immediate (16-bit)
                else:
                    pc += 2
                continue

            if argc == 2:
                pc += 1  # First operand (always register, 8-bit)
                operand = parts[2].lower()
                
                # Second operand: register (8-bit) or immediate (16-bit)
                if operand.startswith("r") or operand in ("sp", "fp", "pc"):
                    pc += 1
                else:
                    pc += 2
        
        # Set entry point
        if self.entry_label:
            if self.entry_label not in self.labels:
                raise ValueError(f"Entry label '{self.entry_label}' not defined")
            self.entry_point = self.labels[self.entry_label]
        else:
            if "start" in self.labels:
                self.entry_point = self.labels["start"]
            else:
                raise ValueError("No .entry directive and no 'start:' label found!")
        
        return pc

    def parse_address_expression(self, expr: str) -> tuple[int, int]:
        """
        Parse address expressions like:
        - [r1 + 100]
        - [r2 - 50]
        - [r3]
        
        Returns: (base_register_code, offset)
        """
        expr = expr.strip()
        
        if expr.startswith('[') and expr.endswith(']'):
            expr = expr[1:-1].strip()
        
        pattern = r'^([a-zA-Z_]\w*)\s*([+\-])\s*(\d+|0x[0-9a-fA-F]+)$'
        match = re.match(pattern, expr)
        
        if match:
            reg, op, value = match.groups()
            
            base_reg = self.get_reg(reg).value
            
            if value.startswith('0x'):
                offset = int(value, 16)
            else:
                offset = int(value)
            
            if op == '-':
                offset = (-offset) & 0xFFFF  # Two's complement for 16-bit
            
            return (base_reg, offset)
        
        simple_pattern = r'^([a-zA-Z_]\w*)$'
        match = re.match(simple_pattern, expr)
        
        if match:
            reg = match.group(1)
            base_reg = self.get_reg(reg).value
            return (base_reg, 0)
        
        raise ValueError(f"Invalid address expression: [{expr}]. Use format: [reg], [reg + offset], or [reg - offset]")

    def parse_load_instruction(self, cs: str, parts: list):
        """
        Parse LOAD instruction: load r1, [r2 +/- offset]
        Supports:
        - load r0, [r1 + 100]
        - load r0, [r1 - 50]
        - load r0, [r1]
        """
        r1_code = self.get_reg(parts[1]).value
        
        bracket_start = cs.find('[')
        bracket_end = cs.find(']')
        
        if bracket_start == -1 or bracket_end == -1:
            raise ValueError(f"LOAD instruction requires bracket syntax: load r1, [address]")
        
        addr_expr = cs[bracket_start:bracket_end + 1]
        r2_code, offset = self.parse_address_expression(addr_expr)
        
        offset_bytes = u16(offset)
        
        # Emit: LOAD opcode, r1, r2, offset (2 bytes)
        load_code = Inst.LOAD.value
        self.program.extend([load_code, r1_code, r2_code, *offset_bytes])
 
    def parse_store_instruction(self, cs: str, parts: list):
        """
        Parse STORE instruction: store [r1 +/- offset], value
        Supports:
        - store [fp - 2], 23        (immediate)
        - store [fp - 4], r0        (register)
        - store [r1 + 100], r2      (register)
        """
        bracket_start = cs.find('[')
        bracket_end = cs.find(']')
        
        if bracket_start == -1 or bracket_end == -1:
            raise ValueError(f"STORE instruction requires bracket syntax: store [address], value")
        
        addr_expr = cs[bracket_start:bracket_end + 1]
        r1_code, offset = self.parse_address_expression(addr_expr)
        
        after_bracket = cs[bracket_end + 1:].strip()
        if after_bracket.startswith(','):
            after_bracket = after_bracket[1:].strip()
        
        value_str = after_bracket.split()[0].strip()
        
        offset_bytes = u16(offset)
        
        if value_str.lower() in REG_TABLE or value_str.lower() in ('sp', 'fp', 'pc'):
            src_code = self.get_reg(value_str).value
            store_code = Inst.STORE_REG.value
            self.program.extend([store_code, r1_code, *offset_bytes, src_code])
        else:
            if value_str.startswith('0x'):
                imm = int(value_str, 16)
            else:
                imm = int(value_str)
            
            imm_bytes = u16(imm)
            store_code = Inst.STORE_IMM.value
            self.program.extend([store_code, r1_code, *offset_bytes, *imm_bytes])

    def parse_line(self,cs:str,idx:int):
        cs = cs.strip('\n')

        if not cs.isnumeric() and ":" in cs:
            pass

        else:
            parts = re.split(r"[,\s]+", cs.strip())

            match parts[0]:
                case 'mov' | 'add' | 'sub' | 'mul' | 'div' | 'and' | 'or':
                    r_code = self.get_reg(parts[1]).value
                    mov_code = self.get_opcode(parts[0],parts).value
                    r_imm_code = self.get_reg_imm(parts[2])                
                    self.program.extend([mov_code,r_code,*as_list(r_imm_code)])
                
                case 'load':
                    self.parse_load_instruction(cs, parts)
                case 'store':
                    self.parse_store_instruction(cs, parts)
                
                case 'inc' | 'dec':
                    inc_code = self.get_opcode('inc',parts).value
                    r_imm_code = self.get_reg_imm(parts[1])
                    self.program.extend([inc_code,r_imm_code])

                # jump inst
                case 'cmp':
                    r_code = self.get_reg(parts[1]).value
                    cmp_code = self.get_opcode('cmp', parts).value
                    r_imm_code = self.get_reg_imm(parts[2])
                    self.program.extend([cmp_code,r_code,*as_list(r_imm_code)])

                case 'jmp' | 'ja' | 'jae' | 'jg' | 'jge':
                    jmp_code = self.get_opcode(parts[0], parts).value
                    lbl = u16(self.labels[parts[1]])
                    self.program.extend([jmp_code,*lbl])
                
                #stack inst
                case 'push' | 'pop':
                    push_code = self.get_opcode(parts[0], parts).value
                    addr = self.get_reg_imm(parts[1])
                    self.program.extend([push_code, *as_list(addr)])
                
                case 'call':
                    call_code = self.get_opcode('call', parts).value
                    addr = u16(self.labels[parts[1]] + 2)
                    print(self.labels[parts[1]] + 2)
                    self.program.extend([call_code,*as_list(addr)])

                case 'ret':
                    ret_code = self.get_opcode('ret', parts).value
                    self.program.append(ret_code)

                case 'hlt':
                    hlt_code = self.get_opcode('hlt', parts)
                    self.program.append(hlt_code.value)
                case ';':
                    pass
                case '.entry':
                    pass
                case _:
                    raise ValueError("Unknown instruction", parts[0])

    def assemble(self):        
        self.pass_label(self.cleaned)
        for idx, line in enumerate(self.cleaned):
            self.parse_line(line,idx)
        
        if self.entry_point is None:
            raise ValueError('Entry point not set (use `.entry <label>`)')

        entry_bytes = u16(self.entry_point + 2)
        full_program = bytearray(entry_bytes) + self.program
        return full_program

    
if __name__ == '__main__':
    content = open("main.ras").readlines()
    ass = Assembler(content)
    bytecode = ass.assemble()

    for i in bytecode:  
        print(i, end=",")

    print("This is",ass.entry_point)

    with open('main.rvm','wb') as f:
        f.write(bytecode)