from anytree import Node
from scanner import get_next_token
from utils.token import TokenType
from firsts import *
from follows import *
from error_follows import *
from codegen import CodeGenerator

received_eof = False
unexpected_eof = False
lookahead = ""
parser_errors = []
cg = CodeGenerator()


def add_syntax_error(error):
    global unexpected_eof
    global parser_errors
    # print(error)
    if "Unexpected" in error:
        unexpected_eof = True
    parser_errors.append(error)


def random_exception():
    raise Exception("Random Exception")


def get_needed_lookahead():
    if lookahead[0] == TokenType.NUM or lookahead[0] == TokenType.ID:
        return str(lookahead[0].name)
    elif lookahead[0] == TokenType.EOF:
        return "$"
    else:
        return lookahead[1]


def match(expected_token, parent):
    global lookahead
    if get_needed_lookahead() == expected_token:
        Node(f"({lookahead[0].name}, {lookahead[1]})", parent=parent)
        lookahead = get_next_token()
    else:
        error = f"#{lookahead[2]} : syntax error, missing {expected_token}"
        add_syntax_error(error)


def initial_parser():
    global lookahead
    lookahead = get_next_token()
    node = program(None)
    if not unexpected_eof:
        if not received_eof:
            Node("$", parent=node)
    return node, parser_errors, cg


def program(parent):
    global received_eof
    global lookahead
    if not parent:
        node = Node("Program")
    else:
        node = Node("Program", parent=parent)

    if get_needed_lookahead() in declaration_list_firsts:
        try:
            declaration_list(node)
        except Exception as e:
            # return node
            raise
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in program_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            program(parent)
    if get_needed_lookahead() == "$":
        Node("$", parent=node)
        received_eof = True
    return node


def declaration_list(parent):
    global lookahead
    node = Node("Declaration-list", parent=parent)

    if get_needed_lookahead() in declaration_firsts:
        declaration(node)
        # print("sadfasf")
        declaration_list(node)
    elif get_needed_lookahead() in declaration_list_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in declaration_list_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            declaration_list(parent)


def declaration(parent):
    global lookahead
    node = Node("Declaration", parent=parent)

    if get_needed_lookahead() in declaration_initial_firsts:
        declaration_initial(node)
        declaration_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in declaration_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Declaration"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            declaration(parent)


def declaration_initial(parent):
    global lookahead
    node = Node("Declaration-initial", parent=parent)

    if get_needed_lookahead() in type_specifier_firsts:
        cg.ptype(lookahead)
        type_specifier(node)
        cg.pid_declare(lookahead)
        match("ID", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in declaration_initial_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Declaration-initial"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            declaration_initial(parent)


def declaration_prime(parent):
    global lookahead
    node = Node("Declaration-prime", parent=parent)

    if get_needed_lookahead() in fun_declaration_prime_firsts:
        fun_declaration_prime(node)
        cg.func_end()
    elif get_needed_lookahead() in var_declaration_prime_firsts:
        var_declaration_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in declaration_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Declaration-prime"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            declaration_prime(parent)


def var_declaration_prime(parent):
    global lookahead
    node = Node("Var-declaration-prime", parent=parent)

    if get_needed_lookahead() == ";":
        cg.declare_variable(lookahead)
        match(";", node)
    elif get_needed_lookahead() == "[":
        match("[", node)
        cg.pnum_v(lookahead)
        match("NUM", node)
        match("]", node)
        cg.declare_array(lookahead)
        match(";", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in var_declaration_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Var-declaration-prime"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            var_declaration_prime(parent)


def fun_declaration_prime(parent):
    global lookahead
    node = Node("Fun-declaration-prime", parent=parent)

    if get_needed_lookahead() == "(":
        cg.declare_new_function()
        match("(", node)
        params(node)
        match(")", node)
        compound_stmt(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in fun_declaration_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Fun-declaration-prime"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            fun_declaration_prime(parent)


def type_specifier(parent):
    global lookahead
    node = Node("Type-specifier", parent=parent)

    if get_needed_lookahead() == "int":
        match("int", node)
    elif get_needed_lookahead() == "void":
        match("void", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in type_specifier_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Type-specifier"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            type_specifier(parent)


def params(parent):
    global lookahead
    node = Node("Params", parent=parent)

    if get_needed_lookahead() == "int":
        cg.ptype(lookahead)
        match("int", node)
        cg.pid_declare(lookahead)
        match("ID", node)
        param_prime(node)
        param_list(node)
    elif get_needed_lookahead() == "void":
        match("void", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in params_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Params"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            params(parent)


def param_list(parent):
    global lookahead
    node = Node("Param-list", parent=parent)

    if get_needed_lookahead() == ",":
        match(",", node)
        param(node)
        param_list(node)
    elif get_needed_lookahead() in param_list_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in param_list_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            param_list(parent)


def param(parent):
    global lookahead
    node = Node("Param", parent=parent)

    if get_needed_lookahead() in declaration_initial_firsts:
        declaration_initial(node)
        param_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in param_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Param"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            param(parent)


def param_prime(parent):
    global lookahead
    node = Node("Param-prime", parent=parent)

    if get_needed_lookahead() == "[":
        match("[", node)
        match("]", node)
        cg.param_arr(lookahead)
    elif get_needed_lookahead() in param_prime_follows:
        Node("epsilon", parent=node)
        cg.param_var(lookahead)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in param_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            param_prime(parent)


def compound_stmt(parent):
    global lookahead
    node = Node("Compound-stmt", parent=parent)

    if get_needed_lookahead() == "{":
        cg.start_scope()
        match("{", node)
        declaration_list(node)
        statement_list(node)
        match("}", node)
        cg.end_scope()
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in compound_stmt_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Compound-stmt"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            compound_stmt(parent)


def statement_list(parent):
    global lookahead
    node = Node("Statement-list", parent=parent)

    if get_needed_lookahead() in statement_firsts:
        statement(node)
        statement_list(node)
    elif get_needed_lookahead() in statement_list_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in statement_list_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            statement_list(parent)


def statement(parent):
    global lookahead
    node = Node("Statement", parent=parent)

    if get_needed_lookahead() in expression_stmt_firsts:
        expression_stmt(node)
    elif get_needed_lookahead() in compound_stmt_firsts:
        compound_stmt(node)
    elif get_needed_lookahead() in selection_stmt_firsts:
        selection_stmt(node)
    elif get_needed_lookahead() in iteration_stmt_firsts:
        iteration_stmt(node)
    elif get_needed_lookahead() in return_stmt_firsts:
        return_stmt(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in statement_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Statement"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            statement(parent)


def expression_stmt(parent):
    global lookahead
    node = Node("Expression-stmt", parent=parent)

    if get_needed_lookahead() in expression_firsts:
        expression(node)
        match(";", node)
        cg.pop()
    elif get_needed_lookahead() == "break":
        match("break", node)
        cg.brek(lookahead)
        match(";", node)
    elif get_needed_lookahead() == ";":
        match(";", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in expression_stmt_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Expression-stmt"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            expression_stmt(parent)


def selection_stmt(parent):
    global lookahead
    node = Node("Selection-stmt", parent=parent)

    if get_needed_lookahead() == "if":
        match("if", node)
        match("(", node)
        expression(node)
        match(")", node)
        cg.save()
        statement(node)
        else_stmt(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in selection_stmt_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Selection-stmt"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            selection_stmt(parent)


def else_stmt(parent):
    global lookahead
    node = Node("Else-stmt", parent=parent)

    if get_needed_lookahead() == "endif":
        match("endif", node)
        cg.jpf()
    elif get_needed_lookahead() == "else":
        cg.jpf_save()
        match("else", node)
        statement(node)
        match("endif", node)
        cg.jp()
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in else_stmt_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Else-stmt"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            else_stmt(parent)


def iteration_stmt(parent):
    global lookahead
    node = Node("Iteration-stmt", parent=parent)

    if get_needed_lookahead() == "for":
        match("for", node)
        match("(", node)
        expression(node)
        match(";", node)
        cg.pop()
        cg.pb_save()
        expression(node)
        cg.save()
        cg.save()
        match(";", node)
        cg.pb_save()
        expression(node)
        cg.pop()
        cg.save()
        match(")", node)
        cg.for_start()
        cg.pb_save()
        statement(node)
        cg.fora()
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in iteration_stmt_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Iteration-stmt"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            iteration_stmt(parent)


def return_stmt(parent):
    global lookahead
    node = Node("Return-stmt", parent=parent)

    if get_needed_lookahead() == "return":
        match("return", node)
        return_stmt_prime(node)
        cg.set_ra()
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in return_stmt_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Return-stmt"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            return_stmt(parent)


def return_stmt_prime(parent):
    global lookahead
    node = Node("Return-stmt-prime", parent=parent)

    if get_needed_lookahead() == ";":
        match(";", node)
    elif get_needed_lookahead() in expression_firsts:
        expression(node)
        cg.set_rv()
        match(";", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in return_stmt_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Return-stmt-prime"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            return_stmt_prime(parent)


def expression(parent):
    global lookahead
    node = Node("Expression", parent=parent)

    if get_needed_lookahead() in simple_expression_zegond_firsts:
        simple_expression_zegond(node)
    elif get_needed_lookahead() == "ID":
        cg.pid(lookahead)
        match("ID", node)
        b(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in expression_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Expression"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            expression(parent)


def b(parent):
    global lookahead
    node = Node("B", parent=parent)

    if get_needed_lookahead() == "=":
        match("=", node)
        expression(node)
        cg.assign()
    elif get_needed_lookahead() == "[":
        match("[", node)
        expression(node)
        match("]", node)
        cg.parr_idx()
        h(node)
    elif get_needed_lookahead() in simple_expression_prime_firsts:
        simple_expression_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in b_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            b(parent)


def h(parent):
    global lookahead
    node = Node("H", parent=parent)

    if get_needed_lookahead() == "=":
        match("=", node)
        expression(node)
        cg.assign()
    elif get_needed_lookahead() in g_firsts:
        g(node)
        d(node)
        c(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in h_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            h(parent)


def simple_expression_zegond(parent):
    global lookahead
    node = Node("Simple-expression-zegond", parent=parent)

    if get_needed_lookahead() in additive_expression_zegond_firsts:
        additive_expression_zegond(node)
        c(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in simple_expression_zegond_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Simple-expression-zegond"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            simple_expression_zegond(parent)


def simple_expression_prime(parent):
    global lookahead
    node = Node("Simple-expression-prime", parent=parent)

    if get_needed_lookahead() in additive_expression_prime_firsts:
        additive_expression_prime(node)
        c(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in simple_expression_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            simple_expression_prime(parent)


def c(parent):
    global lookahead
    node = Node("C", parent=parent)

    if get_needed_lookahead() in relop_firsts:
        relop(node)
        additive_expression(node)
        cg.relop(lookahead)
    elif get_needed_lookahead() in c_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in c_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            c(parent)


def relop(parent):
    global lookahead
    node = Node("Relop", parent=parent)

    if get_needed_lookahead() == "<":
        cg.p_op(lookahead)
        match("<", node)
    elif get_needed_lookahead() == "==":
        cg.p_op(lookahead)
        match("==", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in relop_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Relop"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            relop(parent)


def additive_expression(parent):
    global lookahead
    node = Node("Additive-expression", parent=parent)

    if get_needed_lookahead() in term_firsts:
        term(node)
        d(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in additive_expression_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Additive-expression"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            additive_expression(parent)


def additive_expression_prime(parent):
    global lookahead
    node = Node("Additive-expression-prime", parent=parent)

    if get_needed_lookahead() in term_prime_firsts:
        term_prime(node)
        d(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in additive_expression_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            additive_expression_prime(parent)


def additive_expression_zegond(parent):
    global lookahead
    node = Node("Additive-expression-zegond", parent=parent)

    if get_needed_lookahead() in term_zegond_firsts:
        term_zegond(node)
        d(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in additive_expression_zegond_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Additive-expression-zegond"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            additive_expression_zegond(parent)


def d(parent):
    global lookahead
    node = Node("D", parent=parent)

    if get_needed_lookahead() in addop_firsts:
        addop(node)
        term(node)
        cg.add(lookahead)
        d(node)
    elif get_needed_lookahead() in d_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in d_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            d(parent)


def addop(parent):
    global lookahead
    node = Node("Addop", parent=parent)

    if get_needed_lookahead() == "+":
        cg.p_op(lookahead)
        match("+", node)
    elif get_needed_lookahead() == "-":
        cg.p_op(lookahead)
        match("-", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in addop_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Addop"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            addop(parent)


def term(parent):
    global lookahead
    node = Node("Term", parent=parent)

    if get_needed_lookahead() in signed_factor_firsts:
        signed_factor(node)
        g(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in term_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Term"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            term(parent)


def term_prime(parent):
    global lookahead
    node = Node("Term-prime", parent=parent)

    if get_needed_lookahead() in signed_factor_prime_firsts:
        signed_factor_prime(node)
        g(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in term_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            term_prime(parent)


def term_zegond(parent):
    global lookahead
    node = Node("Term-zegond", parent=parent)

    if get_needed_lookahead() in signed_factor_zegond_firsts:
        signed_factor_zegond(node)
        g(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in term_zegond_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Term-zegond"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            term_zegond(parent)


def g(parent):
    global lookahead
    node = Node("G", parent=parent)

    if get_needed_lookahead() == "*":
        cg.p_op(lookahead)
        match("*", node)
        signed_factor(node)
        cg.mult(lookahead)
        g(node)
    elif get_needed_lookahead() in g_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in g_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            g(parent)


def signed_factor(parent):
    global lookahead
    node = Node("Signed-factor", parent=parent)

    if get_needed_lookahead() == "+":
        cg.p_op(lookahead)
        match("+", node)
        factor(node)
        cg.add(lookahead)
    elif get_needed_lookahead() == "-":
        cg.p_op(lookahead)
        match("-", node)
        factor(node)
        cg.add(lookahead)
    elif get_needed_lookahead() in factor_firsts:
        factor(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in signed_factor_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Signed-factor"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            signed_factor(parent)


def signed_factor_prime(parent):
    global lookahead
    node = Node("Signed-factor-prime", parent=parent)

    if get_needed_lookahead() in factor_prime_firsts:
        factor_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in signed_factor_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            signed_factor_prime(parent)


def signed_factor_zegond(parent):
    global lookahead
    node = Node("Signed-factor-zegond", parent=parent)

    if get_needed_lookahead() == "+":
        cg.p_op(lookahead)
        match("+", node)
        factor(node)
        cg.add(lookahead)
    elif get_needed_lookahead() == "-":
        cg.pzero()
        cg.p_op(lookahead)
        match("-", node)
        factor(node)
        cg.add(lookahead)
    elif get_needed_lookahead() in factor_zegond_firsts:
        factor_zegond(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in signed_factor_zegond_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Signed-factor-zegond"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            signed_factor_zegond(parent)


def factor(parent):
    global lookahead
    node = Node("Factor", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        expression(node)
        match(")", node)
    elif get_needed_lookahead() == "ID":
        cg.pid(lookahead)
        match("ID", node)
        var_call_prime(node)
    elif get_needed_lookahead() == "NUM":
        cg.pnum(lookahead)
        match("NUM", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in factor_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Factor"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            factor(parent)


def var_call_prime(parent):
    global lookahead
    node = Node("Var-call-prime", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        args(node)
        match(")", node)
        cg.call_function(lookahead)
    elif get_needed_lookahead() in var_prime_firsts:
        var_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in var_call_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            var_call_prime(parent)


def var_prime(parent):
    global lookahead
    node = Node("Var-prime", parent=parent)

    if get_needed_lookahead() == "[":
        match("[", node)
        expression(node)
        match("]", node)
        cg.parr_idx()
    elif get_needed_lookahead() in var_prime_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in var_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            var_prime(parent)


def factor_prime(parent):
    global lookahead
    node = Node("Factor-prime", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        args(node)
        match(")", node)
        cg.call_function(lookahead)
    elif get_needed_lookahead() in factor_prime_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in factor_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            factor_prime(parent)


def factor_zegond(parent):
    global lookahead
    node = Node("Factor-zegond", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        expression(node)
        match(")", node)
    elif get_needed_lookahead() == "NUM":
        cg.pnum(lookahead)
        match("NUM", node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in factor_zegond_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Factor-zegonde"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            factor_zegond(parent)


def args(parent):
    global lookahead
    node = Node("Args", parent=parent)

    if get_needed_lookahead() in arg_list_firsts:
        arg_list(node)
    elif get_needed_lookahead() in args_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in args_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            args(parent)


def arg_list(parent):
    global lookahead
    node = Node("Arg-list", parent=parent)

    if get_needed_lookahead() in expression_firsts:
        expression(node)
        arg_list_prime(node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in arg_list_error_follows:
            error = f"#{lookahead[2]} : syntax error, missing Arg-list"
            add_syntax_error(error)
        else:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            arg_list(parent)


def arg_list_prime(parent):
    global lookahead
    node = Node("Arg-list-prime", parent=parent)

    if get_needed_lookahead() == ",":
        match(",", node)
        expression(node)
        arg_list_prime(node)
    elif get_needed_lookahead() in arg_list_prime_follows:
        Node("epsilon", parent=node)
    else:
        node.parent = None
        if get_needed_lookahead() == '$':
            error = f"#{lookahead[2]} : syntax error, Unexpected EOF"
            add_syntax_error(error)
            random_exception()
        if (current_token := get_needed_lookahead()) in arg_list_prime_error_follows:
            error = f"#{lookahead[2]} : syntax error, illegal " + current_token
            add_syntax_error(error)
            lookahead = get_next_token()
            arg_list_prime(parent)
