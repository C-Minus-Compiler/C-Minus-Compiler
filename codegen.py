from codegen_utils.instructions_enum import Instructions
from codegen_utils.semantic_stack import SemanticStack
from codegen_utils.program_block import ProgramBlock
from codegen_utils.semantic_symbol_table import SemanticSymbolTable, SymbolTableEntry, SymbolTableEntryType


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
        t = self.__get_new_temp_variable()
        inst = ThreeAddressCode(Instructions.ASSIGN, f'#{num}', t, '')
        self.program_block.add_block(inst) 
        self.semantic_stack.push(t)
    
    def ptype(self, typ):
        '''Push type from input the semantic stack'''
        self.semantic_stack.push(typ)

    def pid_declare(self, lexeme):
        '''Pops the type of identifier push the address. Adds the new identifier to the symbol table'''
        typ = self.semantic_stack.pop()
        address = self.__get_new_temp_variable()
        entry = SymbolTableEntry(lexeme, address, self.scope_count)
        entry.add_type(SymbolTableEntryType.get_type_by_lexeme(typ))
        self.semantic_symbol_table.insert_entry(entry)
        self.semantic_stack.push(entry.address)
    
    def declare_variable(self):
        '''Pops the variable address from the semantic stack and assigns 0'''
        address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(address) 
        if entry is None:
            # TODO some checks
            return None
        entry.add_type(SymbolTableEntryType.VAR)
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)
 
    def declare_array(self):
        '''Pops array size, address from the semantic stack.'''
        size = self.semantic_stack.pop()
        address = self.semantic_stack.pop()
        self.__increase_temp_pointer(size - 1) # Use -1 because already got a byte in pid_declare
        entry = self.semantic_symbol_table.find_by_address(address)
        if entry is None:
            # TODO some checks
            return None
        entry.add_type(SymbolTableEntryType.ARR)
        entry.set_size(size)
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)

    def assign(self):
        '''
        Pops two last elements of the semantic stack and assign the first one the second
        '''
        value = self.semantic_stack.pop()
        LHS_addr = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.ASSIGN, value, LHS_addr, '')
        self.program_block.add_block(inst)
        self.semantic_stack.push(value)
    
    def parr_idx(self):
        '''
        It is assumed id address and index are on the semantic stack.
        This action pops them and push the address of the element
        '''
        idx = self.semantic_stack.pop()
        id_addr = self.semantic_stack.pop()
        t1 = self.__get_new_temp_variable()
        calcuate_addr_inst1 = ThreeAddressCode(Instructions.MULT, f'#{idx}', '#4', t1)
        self.program_block.add_block(calcuate_addr_inst1)
        t2 = self.__get_new_temp_variable()
        calcuate_addr_inst2 = ThreeAddressCode(Instructions.ADD, t1, id_addr, t2)
        self.program_block.add_block(calcuate_addr_inst2)
        self.semantic_stack.push(t2)

    def p_op(self, op):
        '''
        This method pushs the operator to the semantic stack.
        '''
        self.semantic_stack.push(op)

    def add(self):
        '''
        It is assumed that two operands of the add/sub are on the top. 
        This action add/sub and push the result to the stack
        '''
        o1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        o2 = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()
        if op == '+':
            inst = ThreeAddressCode(Instructions.ADD, o1, o2, t)
        else:
            inst = ThreeAddressCode(Instructions.SUB, o1, o2, t)
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def mult(self):
        '''
        It is assumed that two operands of the add/sub are on the top. 
        This action add/sub and push the result to the stack
        '''
        o1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        o2 = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()
        inst = ThreeAddressCode(Instructions.MULT, o1, o2, t)
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def relop(self):
        '''
        It is assumed that two operands of the add/sub are on the top. 
        This action add/sub and push the result to the stack
        '''
        o1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        o2 = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()
        if op == "==":
            inst = ThreeAddressCode(Instructions.EQ, o1, o2, t)
        else:
            inst = ThreeAddressCode(Instructions.LT, o2, o1, t) # TODO May need to substitute o1 & o2
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)


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

