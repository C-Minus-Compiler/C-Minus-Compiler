class Instruction:
    def __init__(self, inst, op1, op2, op3):
        self.inst = inst 
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3

    def __str__(self):
        return f"({self.inst.value}, {self.op1}, {self.op2}, {self.op3})"
