class Instruction:
    def __init__(self, opcode, operand_1, operand_2, operand_3):
        self.opcode = opcode
        self.operand_1 = operand_1
        self.operand_2 = operand_2
        self.operand_3 = operand_3


class ProgramBlock:
    def __init__(self):
        self.pb_pointer = 0
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        self.pb_pointer += 1

    def increase_pb_pointer(self):
        self.pb_pointer += 1
