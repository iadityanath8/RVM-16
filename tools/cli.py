from assembler import Assembler
import sys 


class CLI:
    def __init__(self, argv:list[str]):
        self.arglist = argv
        self.len     = len(argv)

    def usage(self):
        print("RAS — A Toy Assembler for the RVM-16 Virtual Machine")
        print("----------------------------------------------------\n")
        print("Usage:")
        print("  ras -compile <file>     Assemble the given .ras source file into RVM-16 bytecode")
        print("  ras -help               Show this help message\n")
        print("Examples:")
        print("  ras -compile program.ras")
        print("  ras -help")

    def read_ras(self,file_loc:str):
        file = open(file_loc)
        content = file.read()
        asm = Assembler()
        bytecode = asm.assemble(content)
        self.dump_file(bytecode)

    def parse_cmd(self):
        first = self.arglist[1]
        match first:
            case '-compile':
                if len(self.arglist) == 2:
                    print("----------   command incomplete    --------")
                    self.usage()
                self.read_ras(self.arglist[2])
            case '-help':
                self.usage()
            case _ :
                print("Unknown command")
                self.usage()

    def dump_file(self,bytecode:bytearray):
        with open("output.rvm","wb") as f:
            f.write(bytecode)
            


if __name__ == '__main__':
    cli_parser = CLI(sys.argv)
    cli_parser.parse_cmd()