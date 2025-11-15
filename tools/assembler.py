from instructions import Inst, Reg
import re

INST_TABLE = {
    'mov': {'reg': Inst.MOV_REG, 'imm': Inst.MOV_IMM, 'argc': 2},
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
        
        return ValueError(f"Invalid operand: {cs}")

    def pass_label(self, lines):
        pc = 0

        for line in lines:
            line = line.strip()

            if not line or line.startswith(";") or line.startswith("#"):
                continue

            if line.endswith(":"):
                name = line[:-1].strip()
                self.labels[name] = pc
                continue

            parts = line.replace(",", " ").split()
            inst = parts[0].lower()

            entry = INST_TABLE[inst]
            argc  = entry["argc"]

            pc += 1

            if argc == 0:
                continue

            if argc == 1:
                arg = parts[1].lower()

                if arg in self.labels:  
                    pc += 2
                elif arg.startswith("r"):
                    pc += 1
                else:
                    pc += 2
                continue

            if argc == 2:
                pc += 1

                op2 = parts[2].lower()

                if op2.startswith("r"):
                    pc += 1   
                else:
                    pc += 2   
        return pc


    def parse_line(self,cs:str,idx:int):
        cs = cs.strip('\n')

        if not cs.isnumeric() and ":" in cs:
            pass

        else:
            parts = re.split(r"[,\s]+", cs.strip())

            match parts[0]:
                case 'mov':
                    r_code = self.get_reg(parts[1]).value
                    mov_code = self.get_opcode('mov',parts).value
                    r_imm_code = self.get_reg_imm(parts[2])                
                    self.program.extend([mov_code,r_code,*as_list(r_imm_code)])
                case 'add':
                    r_code = self.get_reg(parts[1]).value
                    add_code = self.get_opcode('add', parts).value
                    r_imm_code = self.get_reg_imm(parts[2])
                    self.program.extend([add_code,r_code,*as_list(r_imm_code)])
                case 'mul':
                    r_code = self.get_reg(parts[1]).value
                    mul_code = self.get_opcode('mul',parts).value
                    r_imm_code = self.get_reg_imm(parts[2])
                    self.program.extend([mul_code,r_code,*as_list(r_imm_code)])
                case 'div':
                    r_code = self.get_reg(parts[1]).value
                    div_code = self.get_opcode('div',parts).value
                    r_imm_code = self.get_reg_imm(parts[2])
                    self.program.extend([div_code,r_code,*as_list(r_imm_code)])
                case 'and':
                    r_code = self.get_reg(parts[1]).value
                    and_code = self.get_opcode('and',parts).value
                    r_imm_code = self.get_reg_imm(parts[2])
                    self.program.extend([and_code,r_code,*as_list(r_imm_code)])
                case 'or':
                    r_code = self.get_reg(parts[1]).value
                    or_code = self.get_opcode('or',parts).value
                    r_imm_code = self.get_reg_imm(parts[2])
                    self.program.extend([or_code,r_code,*as_list(r_imm_code)])    
                
                case 'inc':
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
                case 'push':
                    push_code = self.get_opcode('push', parts).value
                    addr = self.get_reg_imm(parts[1])
                    self.program.extend([push_code, *as_list(addr)])

                case 'pop':
                    pop_code = self.get_opcode('pop',parts).value
                    addr = self.get_reg_imm(parts[1])
                    self.program.extend([pop_code,*as_list(addr)])
                
                case 'call':
                    call_code = self.get_opcode('call', parts).value
                    addr = u16(self.labels[parts[1]])
                    self.program.extend([call_code,*as_list(addr)])

                case 'ret':
                    ret_code = self.get_opcode('ret', parts).value
                    self.program.append(ret_code)

                case 'hlt':
                    hlt_code = self.get_opcode('hlt', parts)
                    self.program.append(hlt_code.value)
                case _:
                    pass

    def assemble(self):        
        self.pass_label(self.cleaned)
        for idx, line in enumerate(self.cleaned):
            self.parse_line(line,idx)
        
        return self.program

    
if __name__ == '__main__':
    content = open("main.ras").readlines()
    ass = Assembler(content)
    bytecode = ass.assemble()

    with open('main.rvm','wb') as f:
        f.write(bytecode)