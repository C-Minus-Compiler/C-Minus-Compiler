from codegen_utils.instructions_enum import Instructions
from codegen_utils.semantic_stack import SemanticStack
from codegen_utils.program_block import ProgramBlock
from codegen_utils.semantic_symbol_table import SemanticSymbolTable


class ThreeAddressCode:
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

    def __get_new_temp_variable(self, size=1):
        temp_variable_address = self.temporary_memory_pointer
        self.temporary_memory_pointer += 4 * size
        return temp_variable_address

    def __increase_temp_pointer(self, size):
        self.temporary_memory_pointer += 4 * size

    def pid(self, variable_name):
        '''Pushs the declared identifier to the semantic stack'''
        symbol = self.semantic_symbol_table.find_variable(variable_name)
        if symbol is None:
            # TODO semantic analyse for the value
            return
        address = symbol[variable_name]
        self.semantic_stack.push(address)

    def pnum(self, num):
        '''Push number from input to the semantic stack'''
        self.semantic_stack.push(num)
    
    def pid_declare(self):
        '''Pops the type of identifier push the address. Adds the new identifier to the symbol table'''
        typ = self.semantic_stack.pop()
        address = self.__get_new_temp_variable()
        # TODO add to symbol table with type
        self.semantic_stack.push(address)
    
    def declare_variable(self):
        '''Pops the variable address from the semantic stack and assigns 0'''
        address = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)
        # TODO set type for the variable as var
 
    def declare_array(self):
        '''Pops array size, address from the semantic stack.'''
        size = self.semantic_stack.pop()
        address = self.semantic_stack.pop()
        self.__increase_temp_pointer(size - 1) # Use -1 because already got a byte in pid_declare
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)
        # TODO get data from data blck using address and set its a array

        
          

    
    def assign_value(self):
        '''Pops two last elements of the semantic stack and assign the first one the second'''
        value = self.semantic_stack.pop()
        identifier = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.ASSIGN, value, identifier, '')
        self.program_block.add_block(inst)
        self.semantic_stack.push(value)


    
        

 
    def prepare_new_function(self):
        inst = ThreeAddressCode(Instructions.ASSIGN, "#4", 0, None)
        self.program_block.add_block(inst)
        self.program_block.add_empty_block()

    def push_in_semantic_stack(self, object):
        self.semantic_stack.push(object)

    def declare_new_function(self):
        function_name = self.semantic_stack.pop()
        function_return_type = self.semantic_stack.pop()
        declared_function = {
            "function_name": function_name,
            "function_return_type": function_return_type,
            "return_address": self.__get_new_temp_variable(),
            "return_value": self.__get_new_temp_variable(),
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
        address = self.__get_new_temp_variable()

        function['variables'].append(
            {"function_variable_name": function_input_variable_name,
             "function_variable_type": function_input_variable_type,
             "address": address})

        self.semantic_stack.push(function)
        self.semantic_symbol_table.insert_variable({function_input_variable_name: address})


    def return_from_function(self):
        return_value = self.semantic_stack.pop()
        function = self.semantic_stack.pop()
        self.semantic_stack.push(function)

        address_of_function_return_value = function[return_value]
        return_address = function['return_address']
        if return_value is not None:
            assign_inst = ThreeAddressCode(Instructions.ASSIGN, return_value,
                                           address_of_function_return_value,
                                           None)
            self.program_block.add_block(assign_inst)

        inst = ThreeAddressCode(Instructions.JP, f"@{return_address}", None, None)
        self.program_block.add_block(inst)

    def pop_function_declaration_from_stack(self):
        function = self.semantic_stack.pop()
        function_name = function['function_name']
        return_address = function['return_address']
        if function_name != 'main':
            inst = ThreeAddressCode(Instructions.JP, f"@{return_address}", None, None)
            self.program_block.add_block(inst)

