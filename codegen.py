from codegen_utils.instructions_enum import Instructions
from codegen_utils.semantic_analys import Function
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

        self.declared_functions = []
        self.current_function = None

        # to handle breaks in for
        self.breaks = []
        self.for_scope = -1

        self.variables_memory_pointer = 100
        self.temporary_memory_pointer = 500

        self.program_block.add_block(ThreeAddressCode(Instructions.ADD, "#4", "0", ""))
        self.program_block.add_empty_block()

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
            return None
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
        '''Pops the type of identifier. Pushs the address. '''
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
        entry = self.semantic_symbol_table.find_by_address(address)
        if entry is None:
            # TODO some checks
            return None
        self.__increase_temp_pointer(size - 1)  # Use -1 because already got a byte in pid_declare
        entry.add_type(SymbolTableEntryType.ARR)
        entry.set_size(size)
        # set the first element to zero
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)
        # set the entry address to the var containing base array as value

    def assign(self):
        '''
        Pops two last elements of the semantic stack and assign the first one the second
        '''
        value = self.semantic_stack.pop()
        LHS_addr = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.ASSIGN, value, LHS_addr, '')
        self.program_block.add_block(inst)
        # self.semantic_stack.push(LHS_addr) # we add this to maintain the assumption for Experssion grammar

    def parr_idx(self):
        '''
        It is assumed variable have the address of array base as value and index are on the semantic stack.
        This action pops them and push the address of the element.
        '''
        idx = self.semantic_stack.pop()
        id_addr = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()
        calcuate_addr_inst1 = ThreeAddressCode(Instructions.MULT, idx, '#4', t)
        self.program_block.add_block(calcuate_addr_inst1)

        entry = self.semantic_symbol_table.find_by_address(id_addr)
        if entry is None:
            # TODO some checks
            return None
        if self.current_function == None or not self.current_function.has_param():
            calcuate_addr_inst2 = ThreeAddressCode(Instructions.ADD, t, f"#{id_addr}", t)
        else:
            calcuate_addr_inst2 = ThreeAddressCode(Instructions.ADD, t, id_addr, t)
        self.program_block.add_block(calcuate_addr_inst2)
        self.semantic_stack.push(f'@{t}')

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
            inst = ThreeAddressCode(Instructions.SUB, o1, o2, t)  # TODO May need to substitute o1 & o2
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
            inst = ThreeAddressCode(Instructions.LT, o2, o1, t)  # TODO May need to substitute o1 & o2
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def save(self):
        '''
        Add an empty bock to the program block and Push the index to the semantic stack
        '''
        self.semantic_stack.push(self.program_block.add_empty_block())

    def jpf_save(self):
        '''
        Sets the instruction at the stored index at stack based on the statement at the top.
        Then add an empty bock to the program block and Push the index to the semantic stack
        '''
        block_idx = self.semantic_stack.pop()
        statement = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.JPF, statement, self.program_block.block_pointer + 1, '')
        self.program_block.set_block(inst, block_idx)
        self.semantic_stack.push(self.program_block.add_empty_block())

    def jpf(self):
        '''
        Sets the instruction at the stored index at stack based on the statement at the top.
        '''
        block_idx = self.semantic_stack.pop()
        statement = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.JPF, statement, self.program_block.block_pointer + 1, '')
        self.program_block.set_block(inst, block_idx)

    def jp(self):
        '''
        Sets the instruction at the stored index at stack based on the statement at the top.
        '''
        block_idx = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, '', '')
        self.program_block.set_block(inst, block_idx)

    def pb_save(self):
        '''
        Just push the program block at the top. Does not increase the block_pointer
        '''
        self.semantic_stack.push(self.program_block.block_pointer)

    def fora(self):
        '''
        Set the jumps on the two former saves.
        First jump unconditionally to the second pb_save. 
        Then jump unconditionally to the for end.
        Then jump unconditionally to the first pb_save.
        Then jump conditionally to the for end.
        Then jump conditionally to the for first.
        Finally handle breaks
        '''
        for_beg_idx = self.semantic_stack.pop()
        exp_end_idx = self.semantic_stack.pop()
        exp_beg_idx = self.semantic_stack.pop()
        cond_end_idx = self.semantic_stack.pop()
        cond_before_end_idx = self.semantic_stack.pop()
        cond_beg_idx = self.semantic_stack.pop()

        for1 = ThreeAddressCode(Instructions.JP, exp_beg_idx, '', '')
        self.program_block.add_block(for1)
        save3 = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, '', '')
        self.program_block.set_block(save3, exp_end_idx)
        for2 = ThreeAddressCode(Instructions.JP, cond_beg_idx, '', '')
        self.program_block.add_block(for2)
        save1 = ThreeAddressCode(Instructions.JPF, self.program_block.block_pointer, '', '')
        self.program_block.set_block(save1, cond_before_end_idx)
        save2 = ThreeAddressCode(Instructions.JP, for_beg_idx, '', '')
        self.program_block.set_block(save2, cond_end_idx)

        for b in self.breaks:
            if b[0] == self.for_scope:
                inst = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, '', '')
                self.program_block.set_block(inst, b)

        self.breaks = [x for x in self.breaks if x[0] == self.for_scope]
        self.for_scope += 1

    def for_start(self):
        '''
        Increases for scopre
        '''
        self.for_scope += 1

    def brek(self):
        '''
        Saves breaks in a differnet
        '''
        if self.for_scope == -1:
            # TODO do some checks
            return None
        tmp = self.program_block.add_empty_block()
        self.breaks.append((self.for_scope, tmp))

    # def define_func(self):
    #     '''
    #     Edits Symbol table entry. Sets program address. Clear types and adds FUNC as new typ
    #     Sets current Functionadn and append to the defined ones
    #     '''
    #     id_addr = self.semantic_stack.pop()
    #     entry = self.semantic_symbol_table.find_by_address(id_addr)
    #     if entry is None:
    #         # TODO do some checs
    #         return None
    #     entry.add_type(SymbolTableEntryType.FUNC)
    #     self.scope_stack.append(id_addr)
    #     self.scope_count += 1
    #
    #     self.__increase_temp_pointer(-1)  # reset the used temporary for the id in the #declre_pid
    #
    #     entry.set_address(self.program_block.block_pointer)
    #     f = Function(entry.lexeme, entry.types[0], self.program_block.block_pointer)
    #     self.current_function = f
    #     self.dec.append(f)

    def param_var(self):
        var_address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(var_address)
        if entry is None:
            # TODO
            return None
        entry.add_type(SymbolTableEntryType.VAR)
        self.current_function["params"].append(entry)

    def param_arr(self):
        var_address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(var_address)
        if entry is None:
            # TODO
            return None
        entry.add_type(SymbolTableEntryType.ARR)
        self.current_function["params"].append(entry)

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
            "pb_address": self.program_block.block_pointer,
            "params": []
        }
        if function_name == 'main':
            jmp_to_main = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, "", "")
            self.program_block.set_block(jmp_to_main, 1)

        self.declared_functions.append(declared_function)
        self.current_function = declared_function

        self.scope_count += 1
        self.scope_stack.append(declared_function["return_address"])

    # def declare_function_input_variable(self):
    #     function_input_variable_name = self.semantic_stack.pop()
    #     function_input_variable_type = self.semantic_stack.pop()
    #     function = self.semantic_stack.pop()
    #     address = self.__get_new_temp_variable()
    #
    #     function['variables'].append(
    #         {"function_variable_name": function_input_variable_name,
    #          "function_variable_type": function_input_variable_type,
    #          "address": address})
    #
    #     self.semantic_stack.push(function)
    #     self.semantic_symbol_table.insert_variable({function_input_variable_name: address})

    def set_rv(self):
        return_value = self.semantic_stack.pop()

        function_return_type = self.current_function["function_return_type"]
        address_of_function_return_value = self.current_function["return_value"]
        if function_return_type == "void":
            # TODO kir mikham
            return None

        assign_inst = ThreeAddressCode(Instructions.ASSIGN, return_value,
                                       address_of_function_return_value,
                                       "")
        self.program_block.add_block(assign_inst)

    def set_ra(self):
        jp_inst = ThreeAddressCode(Instructions.JP, f'@{self.current_function["return_address"]}', '', '')
        self.program_block.add_block(jp_inst)
        self.program_block.add_block(jp_inst)

        self.current_function = None
        self.semantic_symbol_table.table = [x for x in self.semantic_symbol_table.table if x.scope == 1]
        self.scope_count -= 1

    def __find_function_by_lexeme(self, lexeme):
        for func in self.declared_functions:
            if lexeme == func["function_name"]:
                return func
        return None

    def call_function(self):
        """
        push local variables of current function in stack
        """
        args = []
        function = None

        while True:
            temp = self.semantic_stack.pop()
            entry = self.semantic_symbol_table.find_by_address(temp)
            if entry is None:
                args.append(temp)
                continue

            func = self.__find_function_by_lexeme(entry.lexeme)
            if func is None:
                args.append(temp)
            else:
                function = func
                break

        increase_stack_inst = ThreeAddressCode(Instructions.ADD, "#4", "0", "0")
        decrease_stack_inst = ThreeAddressCode(Instructions.SUB, "0", "#4", "0")

        caller_return_address = self.current_function["return_address"]
        push_return_address_to_stack_inst = ThreeAddressCode(Instructions.ASSIGN, caller_return_address, f"@0", "")
        self.program_block.add_block(push_return_address_to_stack_inst)
        self.program_block.add_block(increase_stack_inst)

        local_variables = [x for x in self.semantic_symbol_table.table if x.scope == 1]

        for variable in local_variables:
            variable_address = variable.address
            for i in range(variable.size):
                push_variable_in_stack = ThreeAddressCode(Instructions.ASSIGN, variable_address + (i * 4), f"@0", "")
                self.program_block.add_block(push_variable_in_stack)
                self.program_block.add_block(increase_stack_inst)

        args = args[::-1]
        if len(args) != len(function["params"]):
            # TODO
            return None

        for arg, param in zip(args, function["params"]):
            assign_inst = ThreeAddressCode(Instructions.ASSIGN, arg, param, "")
            self.program_block.add_block(assign_inst)

        callee_return_address = self.program_block.block_pointer + 1 + 2 * (
                sum([x.size for x in local_variables]) + 1)

        jmp_to_callee_inst = ThreeAddressCode(Instructions.JP, callee_return_address, "", "")
        self.program_block.add_block(jmp_to_callee_inst)

        return_value_of_callee = self.__get_new_temp_variable()
        assign_return_val = ThreeAddressCode(Instructions.ASSIGN, function["return_value"], return_value_of_callee, "")
        self.program_block.add_block(assign_return_val)
        self.semantic_stack.push(return_value_of_callee)

        local_variables = local_variables[::-1]
        for variable in local_variables:
            for i in reversed(range(variable.size)):
                self.program_block.add_block(decrease_stack_inst)
                inst = ThreeAddressCode(Instructions.ASSIGN, "@0", variable.address + (i * 4), "")
                self.program_block.add_block(inst)

        # def pop_function_declaration_from_stack(self):
        #     function = self.semantic_stack.pop()
        #     function_name = function['function_name']
        #     return_address = function['return_address']
        #     if function_name != 'main':
        #         inst = ThreeAddressCode(Instructions.JP, f"@{return_address}", None, None)
        #         self.program_block.add_block(inst)
