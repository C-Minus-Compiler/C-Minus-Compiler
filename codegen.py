from codegen_utils.instructions_enum import Instructions
from codegen_utils.semantic_stack import SemanticStack
from codegen_utils.program_block import ProgramBlock
from codegen_utils.semantic_symbol_table import SemanticSymbolTable


class ThreeAddressCodeGenerator:
    def __init__(self, instruction, op1, op2, op3):
        self.instruction = instruction
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3

    def __str__(self):
        return f"#({self.instruction}, {self.op1}, {self.op2}, {self.op3})"


class CodeGenerator:
    def __init__(self):
        self.semantic_stack = SemanticStack()
        self.program_block = ProgramBlock()
        self.semantic_symbol_table = SemanticSymbolTable()
        self.scope_count = 0
        self.scope_stack = []
        self.variables_memory_pointer = 100
        self.temporary_memory_pointer = 500

    def create_three_address_code(self, instruction, op1, op2, op3):
        return ThreeAddressCodeGenerator(instruction, op1, op2, op3)

    def prepare_new_function(self):
        self.program_block.add_block(self.create_three_address_code(Instructions.ASSIGN, "#4", 0, None))
        self.program_block.add_empty_block()

    def push_in_semantic_stack(self, object):
        self.semantic_stack.push(object)

    def get_new_temp_variable(self):
        temp_variable_address = self.temporary_memory_pointer
        self.temporary_memory_pointer += 4
        return temp_variable_address

    def declare_new_function(self):
        function_name = self.semantic_stack.pop()
        function_return_type = self.semantic_stack.pop()
        declared_function = {
            "function_name": function_name,
            "function_return_type": function_return_type,
            "return_address": self.get_new_temp_variable(),
            "return_value": self.get_new_temp_variable(),
            "variables": []
        }
        if function_name == 'main':
            pass
        # TODO set jp in program block line 2
        # self.program_block.change_line(
        #     1,
        #     self.program_block.jp,
        #     self.program_block.get_current_line() + 1,
        # )

        self.semantic_stack.push(declared_function)

    def declare_function_input_variable(self):
        function_input_variable_name = self.semantic_stack.pop()
        function_input_variable_type = self.semantic_stack.pop()
        function = self.semantic_stack.pop()
        address = self.get_new_temp_variable()

        function['variables'].append(
            {"function_variable_name": function_input_variable_name,
             "function_variable_type": function_input_variable_type,
             "address": address})

        self.semantic_stack.push(function)
        self.semantic_symbol_table.insert_variable({function_input_variable_name: address})

    def pid(self, variable_name):
        symbol = self.semantic_symbol_table.find_variable(variable_name)
        address = symbol[variable_name]
        self.semantic_stack.push(address)

    def return_from_function(self):
        return_value = self.semantic_stack.pop()
        function = self.semantic_stack.pop()
        self.semantic_stack.push(function)

        address_of_function_return_value = function[return_value]
        return_address = function['return_address']
        if return_value is not None:
            assign_block = self.create_three_address_code(Instructions.ASSIGN, return_value,
                                                          address_of_function_return_value,
                                                          None)
            self.program_block.add_block(assign_block)

        block = self.create_three_address_code(Instructions.JP, f"@{return_address}", None, None)
        self.program_block.add_block(block)

    def pop_function_declaration_from_stack(self):
        function = self.semantic_stack.pop()
        function_name = function['function_name']
        return_address = function['return_address']
        if function_name != 'main':
            block = self.create_three_address_code(Instructions.JP, f"@{return_address}", None, None)
            self.program_block.add_block(block)

    def push_number(self, num):
        self.semantic_stack.push(num)

    def assign_value(self):
        symbol = self.semantic_stack.pop()
        exp = self.semantic_stack.pop()
        assign_block = self.create_three_address_code(Instructions.ASSIGN, symbol, exp, None)
        self.program_block.add_block(assign_block)
        self.semantic_stack.push(exp)
