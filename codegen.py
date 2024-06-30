from codegen_utils.instructions_enum import Instructions
from codegen_utils.semantic_stack import SemanticStack
from codegen_utils.program_block import ProgramBlock
from codegen_utils.semantic_symbol_table import SemanticSymbolTable, SymbolTableEntry, SymbolTableEntryType
import inspect


class ThreeAddressCode:
    def __init__(self, instruction, op1, op2, op3):
        self.instruction = instruction
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3

    def __str__(self):
        return f"	({self.instruction.value}, {self.op1}, {self.op2}, {self.op3})"


class CodeGenerator:
    def __init__(self):
        self.semantic_stack = SemanticStack()
        self.program_block = ProgramBlock()
        self.semantic_symbol_table = SemanticSymbolTable()

        self.semantic_symbol_table.insert_entry(SymbolTableEntry("output", 0, 0))

        self.func_declared = False
        self.scope_count = 0
        self.scope_stack = []

        self.declared_functions = [{"function_name": "output"}]
        self.current_function = None

        # to handle breaks in for
        self.breaks = []
        self.for_scope = -1

        self.semantic_errors = []
        self.variables_memory_pointer = 100
        self.function_private_temps_pointer = 1000
        self.temporary_memory_pointer = 2000

        self.program_block.add_block(ThreeAddressCode(Instructions.ASSIGN, "#4", "0", ""))
        self.program_block.add_empty_block()

    def __scope_semantic_error_msg(self, line_num, name):
        return f"#{line_num} : Semantic Error! '{name}' is not defined."

    def __args_len_mismatch_semantic_error_msg(self, line_num, name):
        return f"#{line_num} : Semantic Error! Mismatch in numbers of arguments of '{name}'."

    def __no_for_break(self, line_num):
        return f"#{line_num} : Semantic Error! No 'for' found for 'break'."

    def __illegal_type_semantic_error_msg(self, line_num, name):
        return f"#{line_num} : Semantic Error! Illegal type of void for '{name}'."

    def __type_missmatch_in_operands(self, line_num, expected, actual):
        return f"#{line_num} : Semantic Error! Type mismatch in operands, Got {actual} instead of {expected}."

    def __missmatch_in_function_param(self, line_num, param_num, func_name, expected, actual):
        return f"#{line_num} : Semantic Error! Mismatch in type of argument {param_num} of '{func_name}'. Expected '{expected}' but got '{actual}' instead."

    def __print_message(self, message):
        # pass
        print(message)

    def __get_new_temp_variable(self, size=1):
        temp_variable_address = self.temporary_memory_pointer
        self.temporary_memory_pointer += 4 * size
        return temp_variable_address

    def __increase_temp_pointer(self, size):
        self.temporary_memory_pointer += 4 * size

    def __get_new_private_temp(self):
        tmp = self.function_private_temps_pointer
        self.function_private_temps_pointer += 4
        return tmp

    def __is_arr(self, op):
        entry = self.semantic_symbol_table.find_by_address(op)
        if entry and SymbolTableEntryType.ARR in entry.types:
            return True
        return False


    def pop(self):
        self.__print_message(inspect.stack()[0][3])
        self.semantic_stack.pop()

    def pid(self, lookahead):
        '''Pushs the declared identifier to the semantic stack'''
        self.__print_message(inspect.stack()[0][3])
        variable_name = lookahead[1]
        line_number = lookahead[2]
        entry = self.semantic_symbol_table.find_variable(variable_name)
        if entry is None:
            self.semantic_errors.append(self.__scope_semantic_error_msg(line_number, variable_name))
            # push dummy
            self.semantic_stack.push(0)
            return
        address = entry.address
        self.semantic_stack.push(address)

    def pnum(self, lookahead):
        '''Push number from input to the semantic stack'''
        self.__print_message(inspect.stack()[0][3])
        num = lookahead[1]
        t = self.__get_new_temp_variable()
        inst = ThreeAddressCode(Instructions.ASSIGN, f'#{num}', t, '')
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def pnum_v(self, lookahead):
        '''Push number from input to the semantic stack'''
        num = lookahead[1]
        self.__print_message(inspect.stack()[0][3])
        self.semantic_stack.push(int(num))

    def pzero(self):
        self.__print_message(inspect.stack()[0][3])
        t = self.__get_new_temp_variable()
        inst = ThreeAddressCode(Instructions.ASSIGN, f'#0', t, '')
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def ptype(self, lookahead):
        '''Push type from input the semantic stack'''
        typ = lookahead[1]
        self.__print_message(inspect.stack()[0][3])
        self.semantic_stack.push(typ)

    def pid_declare(self, lookahead):
        '''Pops the type of identifier. Pushs the address. '''
        self.__print_message(inspect.stack()[0][3])
        lexeme = lookahead[1]
        line_number = lookahead[2]
        typ = self.semantic_stack.pop()
        address = self.__get_new_temp_variable()
        entry = SymbolTableEntry(lexeme, address, self.scope_count)
        entry.add_type(SymbolTableEntryType.get_type_by_lexeme(typ))
        self.semantic_symbol_table.insert_entry(entry)
        self.semantic_stack.push(entry.address)

    def declare_variable(self, lookahead):
        '''Pops the variable address from the semantic stack and assigns 0'''
        self.__print_message(inspect.stack()[0][3])
        line_number = lookahead[2]
        address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(address)
        if entry is None:
            # TODO some checks
            return None
        if SymbolTableEntryType.VOID in entry.types:
            self.semantic_errors.append(self.__illegal_type_semantic_error_msg(line_number, entry.lexeme))
            return
        entry.add_type(SymbolTableEntryType.VAR)
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)

    def declare_array(self, lookahead):
        '''Pops array size, address from the semantic stack.'''
        self.__print_message(inspect.stack()[0][3])
        line_number = lookahead[2]
        size = self.semantic_stack.pop()
        address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(address)
        if entry is None:
            # TODO some checks
            return None
        if SymbolTableEntryType.VOID in entry.types:
            self.semantic_errors.append(self.__illegal_type_semantic_error_msg(line_number, entry.lexeme))
            return
        self.__increase_temp_pointer(size - 1)  # Use -1 because already got a byte in pid_declare
        entry.add_type(SymbolTableEntryType.ARR)
        entry.set_size(size)
        # set the first element to zero
        inst = ThreeAddressCode(Instructions.ASSIGN, '#0', address, '')
        self.program_block.add_block(inst)
        # set the entry address to the var containing base array as value

    def assign(self, lookahead):
        '''
        Pops two last elements of the semantic stack and assign the first one the second
        '''
        self.__print_message(inspect.stack()[0][3])
        line_num = lookahead[2]
        value = self.semantic_stack.pop()
        LHS_addr = self.semantic_stack.pop()

        lhs_entry = self.semantic_symbol_table.find_by_address(LHS_addr)
        if lhs_entry is None and not (isinstance(LHS_addr, str) and LHS_addr.startswith("@")):
            self.semantic_stack.push(0)
            return

        if self.__is_arr(LHS_addr) != self.__is_arr(value):
            expected = 'array' if self.__is_arr(value) else 'int'
            actual = 'array' if self.__is_arr(LHS_addr) else 'int'
            self.semantic_errors.append(self.__type_missmatch_in_operands(line_num, expected, actual))

        inst = ThreeAddressCode(Instructions.ASSIGN, value, LHS_addr, '')
        self.program_block.add_block(inst)
        self.semantic_stack.push(LHS_addr)  # we add this to maintain the assumption for Experssion grammar

    def __current_function_has_param(self, lexeme):
        for entry in self.current_function["params"]:
            if entry.lexeme == lexeme:
                return True
        return False

    def parr_idx(self):
        '''
        It is assumed variable have the address of array base as value and index are on the semantic stack.
        This action pops them and push the address of the element.
        '''
        self.__print_message(inspect.stack()[0][3])
        idx = self.semantic_stack.pop()
        id_addr = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()
        calcuate_addr_inst1 = ThreeAddressCode(Instructions.MULT, idx, '#4', t)
        self.program_block.add_block(calcuate_addr_inst1)

        entry = self.semantic_symbol_table.find_by_address(id_addr)
        if entry is None:
            # TODO some checks
            return None
        if self.current_function is None or not self.__current_function_has_param(entry.lexeme):
            calcuate_addr_inst2 = ThreeAddressCode(Instructions.ADD, t, f"#{id_addr}", t)
        else:
            calcuate_addr_inst2 = ThreeAddressCode(Instructions.ADD, t, id_addr, t)
        self.program_block.add_block(calcuate_addr_inst2)
        self.semantic_stack.push(f'@{t}')

    def p_op(self, lookahead):
        '''
        This method pushs the operator to the semantic stack.
        '''
        op = lookahead[1]
        self.__print_message(inspect.stack()[0][3])
        self.semantic_stack.push(op)

    def add(self, lookahead):
        '''
        It is assumed that two operands of the add/sub are on the top. 
        This action add/sub and push the result to the stack
        '''
        self.__print_message(inspect.stack()[0][3])
        line_num = lookahead[2]
        o1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        o2 = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()
        if op == '+':
            inst = ThreeAddressCode(Instructions.ADD, o1, o2, t)
        else:
            inst = ThreeAddressCode(Instructions.SUB, o2, o1, t)

        if self.__is_arr(o1) or self.__is_arr(o2):
            self.semantic_errors.append(self.__type_missmatch_in_operands(line_num, 'int', 'array'))
            #dummy push
            self.semantic_stack.push(0)
            return


        # if o1 == 1004 and o2 == 1000:
        #     self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, '#5000', '', ''))
        #     self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, o1, '', ''))
        #     self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, o2, '', ''))
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def mult(self, lookahead):
        '''
        It is assumed that two operands of the add/sub are on the top. 
        This action add/sub and push the result to the stack
        '''
        self.__print_message(inspect.stack()[0][3])
        line_num = lookahead[2]
        o1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        o2 = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()

        if self.__is_arr(o1) or self.__is_arr(o2):
            self.semantic_errors.append(self.__type_missmatch_in_operands(line_num, 'int', 'array'))
            #dummy push
            self.semantic_stack.push(0)
            return

        inst = ThreeAddressCode(Instructions.MULT, o1, o2, t)
        self.program_block.add_block(inst)
        self.semantic_stack.push(t)

    def relop(self, lookahead):
        '''
        It is assumed that two operands of the add/sub are on the top. 
        This action add/sub and push the result to the stack
        '''
        self.__print_message(inspect.stack()[0][3])
        line_num = lookahead[2]
        o1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        o2 = self.semantic_stack.pop()
        t = self.__get_new_temp_variable()

        if self.__is_arr(o1) or self.__is_arr(o2):
            self.semantic_errors.append(self.__type_missmatch_in_operands(line_num, 'int', 'array'))
            #dummy push
            self.semantic_stack.push(0)
            return

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
        self.__print_message(inspect.stack()[0][3])
        self.semantic_stack.push(self.program_block.add_empty_block())

    def jpf_save(self):
        '''
        Sets the instruction at the stored index at stack based on the statement at the top.
        Then add an empty bock to the program block and Push the index to the semantic stack
        '''
        self.__print_message(inspect.stack()[0][3])
        block_idx = self.semantic_stack.pop()
        statement = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.JPF, statement, self.program_block.block_pointer + 1, '')
        self.program_block.set_block(inst, block_idx)
        self.semantic_stack.push(self.program_block.add_empty_block())

    def jpf(self):
        '''
        Sets the instruction at the stored index at stack based on the statement at the top.
        '''
        self.__print_message(inspect.stack()[0][3])
        block_idx = self.semantic_stack.pop()
        statement = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.JPF, statement, self.program_block.block_pointer, '')
        self.program_block.set_block(inst, block_idx)

    def jp(self):
        '''
        Sets the instruction at the stored index at stack based on the statement at the top.
        '''
        self.__print_message(inspect.stack()[0][3])
        block_idx = self.semantic_stack.pop()
        inst = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, '', '')
        self.program_block.set_block(inst, block_idx)

    def pb_save(self):
        '''
        Just push the program block at the top. Does not increase the block_pointer
        '''
        self.__print_message(inspect.stack()[0][3])
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
        self.__print_message(inspect.stack()[0][3])
        for_beg_idx = self.semantic_stack.pop()
        exp_end_idx = self.semantic_stack.pop()
        exp_beg_idx = self.semantic_stack.pop()
        cond_end_idx = self.semantic_stack.pop()
        cond_before_end_idx = self.semantic_stack.pop()
        cond_value = self.semantic_stack.pop()
        cond_beg_idx = self.semantic_stack.pop()

        for1 = ThreeAddressCode(Instructions.JP, exp_beg_idx, '', '')
        self.program_block.add_block(for1)
        save3 = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, '', '')
        self.program_block.set_block(save3, exp_end_idx)
        for2 = ThreeAddressCode(Instructions.JP, cond_beg_idx, '', '')
        self.program_block.add_block(for2)
        save1 = ThreeAddressCode(Instructions.JPF, cond_value, self.program_block.block_pointer, '')
        self.program_block.set_block(save1, cond_before_end_idx)
        save2 = ThreeAddressCode(Instructions.JP, for_beg_idx, '', '')
        self.program_block.set_block(save2, cond_end_idx)

        for b in self.breaks:
            if b[0] == self.for_scope:
                self.__print_message(f'scope: {b[0]}, brea{b[1]}, to: {self.program_block.block_pointer}')
                inst = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, '', '')
                self.program_block.set_block(inst, b[1])

        self.breaks = [x for x in self.breaks if x[0] != self.for_scope]
        self.for_scope -= 1

    def for_start(self):
        '''
        Increases for scopre
        '''
        self.__print_message(inspect.stack()[0][3])
        self.for_scope += 1
        pass

    def brek(self, lookahead):
        '''
        Saves breaks in a differnet
        '''
        self.__print_message(inspect.stack()[0][3])
        line_num = lookahead[2]
        if self.for_scope == -1:
            self.semantic_errors.append(self.__no_for_break(line_num))
            return None
        tmp = self.program_block.add_empty_block()
        self.breaks.append((self.for_scope, tmp))

    def param_var(self, lookahead):
        self.__print_message(inspect.stack()[0][3])
        line_number = lookahead[2]
        var_address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(var_address)
        if entry is None:
            # TODO
            return None

        if SymbolTableEntryType.VOID in entry.types:
            self.semantic_errors.append(self.__illegal_type_semantic_error_msg(line_number, entry.lexeme))
            return
        entry.add_type(SymbolTableEntryType.VAR)
        self.current_function["params"].append(entry)

    def param_arr(self, lookahead):
        self.__print_message(inspect.stack()[0][3])
        line_number = lookahead[2]
        var_address = self.semantic_stack.pop()
        entry = self.semantic_symbol_table.find_by_address(var_address)
        if entry is None:
            # TODO
            return None

        if SymbolTableEntryType.VOID in entry.types:
            self.semantic_errors.append(self.__illegal_type_semantic_error_msg(line_number, entry.lexeme))
            return
        entry.add_type(SymbolTableEntryType.ARR)
        self.current_function["params"].append(entry)

    def prepare_new_function(self):
        self.__print_message(inspect.stack()[0][3])
        inst = ThreeAddressCode(Instructions.ASSIGN, "#4", 0, None)
        self.program_block.add_block(inst)
        self.program_block.add_empty_block()

    def push_in_semantic_stack(self, object):
        self.__print_message(inspect.stack()[0][3])
        self.semantic_stack.push(object)

    def declare_new_function(self):
        self.__print_message(inspect.stack()[0][3])
        self.__increase_temp_pointer(-1)

        function_name = (x := self.semantic_symbol_table.find_by_address(self.semantic_stack.pop())).lexeme
        function_return_type = x.types[0]
        x.types.append(SymbolTableEntryType.FUNC)
        declared_function = {
            "function_name": function_name,
            "function_return_type": function_return_type,
            "return_address": self.__get_new_temp_variable(),
            "return_value": self.__get_new_temp_variable(),
            "pb_address": self.program_block.block_pointer,
            "params": [],
            "function_temps": [],
            "push_idxs": [],
            "pop_idxs": []
        }
        if function_name == 'main':
            jmp_to_main = ThreeAddressCode(Instructions.JP, self.program_block.block_pointer, "", "")
            self.program_block.set_block(jmp_to_main, 1)
            self.program_block.add_block(
                ThreeAddressCode(Instructions.ASSIGN, 0, declared_function["return_address"], ""))
            for i in range(10):
                self.program_block.add_block(ThreeAddressCode(Instructions.ASSIGN, "#0", f'{1000 + i * 4}', ''))

        self.declared_functions.append(declared_function)
        self.current_function = declared_function

        self.scope_count += 1
        self.func_declared = True
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
        self.__print_message(inspect.stack()[0][3])
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
        self.__print_message(inspect.stack()[0][3])
        jp_inst = ThreeAddressCode(Instructions.JP, f'@{self.current_function["return_address"]}', '', '')
        self.program_block.add_block(jp_inst)
        self.program_block.add_block(jp_inst)

    def func_end(self):
        self.__print_message(inspect.stack()[0][3])
        if self.current_function["function_name"] != "main":
            jp_inst = ThreeAddressCode(Instructions.JP, f'@{self.current_function["return_address"]}', '', '')
            self.program_block.add_block(jp_inst)
            self.program_block.add_block(jp_inst)

        self.function_private_temps_pointer = 1000
        self.current_function = None
        # self.semantic_symbol_table.table = [x for x in self.semantic_symbol_table.table if x.scope == 0]
        # self.scope_count -= 1

    def start_scope(self):
        if self.func_declared:
            self.func_declared = False
        else:
            self.scope_count += 1

    def end_scope(self):
        self.semantic_symbol_table.table = [x for x in self.semantic_symbol_table.table if x.scope != self.scope_count]
        self.scope_count -= 1
        pass

    def __find_function_by_lexeme(self, lexeme):
        for func in self.declared_functions:
            if lexeme == func["function_name"]:
                return func
        return None

    def call_function(self, lookahead):
        """
        push local variables of current function in stack
        """
        self.__print_message(inspect.stack()[0][3])
        line_number = lookahead[2]
        args = []
        function = None

        while True:
            try:
                temp = self.semantic_stack.pop()
            except Exception as e:
                # TODO not defined function errror
                return
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

        self.__print_message(f'=====function: {function["function_name"]} pb: {self.program_block.block_pointer}')

        if function["function_name"] == "output":
            if len(args) != 1:
                # TODO
                return None
            self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, args[0], "", ""))
            self.semantic_stack.push(args[0])
            return

        increase_stack_inst = ThreeAddressCode(Instructions.ADD, "#4", "0", "0")
        decrease_stack_inst = ThreeAddressCode(Instructions.SUB, "0", "#4", "0")

        caller_return_address = self.current_function["return_address"]
        push_return_address_to_stack_inst = ThreeAddressCode(Instructions.ASSIGN, caller_return_address, "@0", "")
        self.program_block.add_block(push_return_address_to_stack_inst)
        self.program_block.add_block(increase_stack_inst)

        # dummy assign to return value of caller

        caller_return_value = self.current_function["return_value"]
        self.program_block.add_block(ThreeAddressCode(Instructions.ASSIGN, "#0", caller_return_value, ""))
        push_return_value_to_stack_inst = ThreeAddressCode(Instructions.ASSIGN, caller_return_value, "@0", "")
        self.program_block.add_block(push_return_value_to_stack_inst)
        self.program_block.add_block(increase_stack_inst)

        local_variables = [x for x in self.semantic_symbol_table.table if x.scope == 1]

        for variable in local_variables:
            variable_address = variable.address
            for i in range(variable.size):
                push_variable_in_stack = ThreeAddressCode(Instructions.ASSIGN, variable_address + (i * 4), "@0", "")
                self.program_block.add_block(push_variable_in_stack)
                self.program_block.add_block(increase_stack_inst)

        for i in range(10):
            push_variable_in_stack = ThreeAddressCode(Instructions.ASSIGN, 1000 + (i * 4), "@0", "")
            self.program_block.add_block(push_variable_in_stack)
            self.program_block.add_block(increase_stack_inst)

        args = args[::-1]
        if len(args) != len(function["params"]):
            self.semantic_errors.append(
                self.__args_len_mismatch_semantic_error_msg(line_number, function["function_name"]))

            # dummy push
            self.semantic_stack.push(0)
            return

        for i, pack in enumerate(zip(args, function["params"])):
            arg, param = pack
            if self.__is_arr(arg) != (SymbolTableEntryType.ARR in param.types):
                expected = 'array' if SymbolTableEntryType.ARR in param.types else 'int'
                actual = 'array' if self.__is_arr(arg) else 'int'
                self.semantic_errors.append(self.__missmatch_in_function_param(line_number, i+1, function["function_name"], expected, actual))
                # dummy push
                self.semantic_stack.push(0)
                return
            if SymbolTableEntryType.ARR in param.types and not self.__current_function_has_param(param.lexeme):
                assign_inst = ThreeAddressCode(Instructions.ASSIGN, f"#{arg}", param.address, "")
            else:
                assign_inst = ThreeAddressCode(Instructions.ASSIGN, arg, param.address, "")
            self.program_block.add_block(assign_inst)

        callee_return_address = self.program_block.block_pointer + 2
        callee_return_address_assignment_inst = ThreeAddressCode(Instructions.ASSIGN, f"#{callee_return_address}",
                                                                 function["return_address"], "")
        self.program_block.add_block(callee_return_address_assignment_inst)

        # callee_return_address = self.program_block.block_pointer + 1 + 2 * (
        #         sum([x.size for x in local_variables]) + 1)

        jmp_to_callee_inst = ThreeAddressCode(Instructions.JP, function["pb_address"], "", "")
        self.program_block.add_block(jmp_to_callee_inst)

        if function["function_return_type"] != SymbolTableEntryType.VOID:
            # return_value_of_callee = self.__get_new_private_temp()
            return_value_of_callee = self.__get_new_temp_variable()
            self.current_function["function_temps"].append(return_value_of_callee)
            assign_return_val = ThreeAddressCode(Instructions.ASSIGN, function["return_value"], return_value_of_callee,
                                                 "")
            self.program_block.add_block(assign_return_val)

            addrrr = self.semantic_symbol_table.find_by_lexeme('a')
            # if addrrr is not None:
            #     self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, '#5000', '', ''))
            #     self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, addrrr.address, '', ''))
            #     self.program_block.add_block(ThreeAddressCode(Instructions.PRINT, return_value_of_callee, '', ''))

            self.semantic_stack.push(return_value_of_callee)
        else:
            dummy = "0"
            self.semantic_stack.push(dummy)

        for i in reversed(range(10)):
            self.program_block.add_block(decrease_stack_inst)
            pop_variable_in_stack = ThreeAddressCode(Instructions.ASSIGN, "@0", 1000 + (i * 4), "")
            self.program_block.add_block(pop_variable_in_stack)

        local_variables = local_variables[::-1]
        for variable in local_variables:
            for i in reversed(range(variable.size)):
                self.program_block.add_block(decrease_stack_inst)
                inst = ThreeAddressCode(Instructions.ASSIGN, "@0", variable.address + (i * 4), "")
                self.program_block.add_block(inst)

        self.program_block.add_block(decrease_stack_inst)
        pop_return_value_to_stack_inst = ThreeAddressCode(Instructions.ASSIGN, "@0", caller_return_value, "")
        self.program_block.add_block(pop_return_value_to_stack_inst)

        self.program_block.add_block(decrease_stack_inst)
        pop_return_address_to_stack_inst = ThreeAddressCode(Instructions.ASSIGN, "@0", caller_return_address, "")
        self.program_block.add_block(pop_return_address_to_stack_inst)
