"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.running = True
        self.fl = 0b00000000
        # set up branch table
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE

    def ram_read(self, mar):  # accept Memory Address Register (MAR)
        return self.ram[mar]

    def ram_write(self, mar, mdr):  # accept Memory Data Register (MDR)
        self.ram[mar] = mdr

    def load(self, file_name):
        """Load a program into memory."""

        address = 0
        try:
            with open(file_name) as file:
                for line in file:
                    split_line = line.split("#")[0]
                    command = split_line.strip()
                    if command == "":
                        continue
                    instruction = int(command, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} file was not found")
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

    def handle_HLT(self):
        self.running = False

    def handle_LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b

    def handle_PRN(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])

    def handle_ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)

    def handle_MUL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)

    def handle_PUSH(self):
        # decrement the stack pointer
        self.reg[7] -= 1
        # get a value from the given register
        register = self.ram_read(self.pc + 1)
        value = self.reg[register]
        # put the value at the stack address
        sp = self.reg[7]
        self.ram[sp] = value

    def handle_POP(self):
        # get the stack pointer address
        sp = self.reg[7]
        # get a value from the given register
        register = self.ram_read(self.pc + 1)
        # use stack pointer to get the value
        value = self.ram[sp]
        # put the value into given register
        self.reg[register] = value
        # increment stack pointer
        self.reg[7] += 1

    def handle_CALL(self):
        # get the register number
        reg = self.ram_read(self.pc + 1)
        # get the address to jump to, from the register
        address = self.reg[reg]
        # push command after CALL onto the stack
        return_address = self.pc + 2
        # decrement stack pointer
        self.reg[7] -= 1
        sp = self.reg[7]
        # put return address on the stack
        self.ram[sp] = return_address
        # look at register, jump to the address
        self.pc = address

    def handle_RET(self):
        # pop the return address off the stack
        sp = self.reg[7]
        return_address = self.ram[sp]
        self.reg[7] += 1
        # go the return address: set the pc to return address
        self.pc = return_address

    def handle_CMP(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("CMP", operand_a, operand_b)

    def handle_JMP(self):
        reg = self.ram_read(self.pc + 1)
        address = self.reg[reg]
        self.pc = address

    def handle_JEQ(self):
        reg = self.ram_read(self.pc + 1)
        address = self.reg[reg]
        if self.fl == 0b00000001:
            self.pc = address
        else:
            self.pc += 2

    def handle_JNE(self):
        reg = self.ram_read(self.pc + 1)
        address = self.reg[reg]
        if self.fl != 0b00000001:
            self.pc = address
        else:
            self.pc += 2

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)  # Instruction Register
            value = ir
            op_count = value >> 6
            ir_length = 1 + op_count
            self.branchtable[ir]()
            if ir == 0 or None:
                print(f"Unknown Instruction: {ir}")
                sys.exit()
            if ir != CALL and ir != RET and ir != JMP and ir != JEQ and ir != JNE:
                self.pc += ir_length
