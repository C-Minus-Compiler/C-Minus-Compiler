from anytree import Node
from scanner import get_next_token
from utils.token import TokenType
from firsts import *
from follows import *

lookahead = ""


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
        random_exception()


def initial_parser():
    global lookahead
    lookahead = get_next_token()
    node = program()
    return node


def program():
    node = Node("Program")

    if get_needed_lookahead() in declaration_list_firsts:
        declaration_list(node)
    if get_needed_lookahead() == "$":
        Node("$", parent=node)
    return node


def declaration_list(parent):
    node = Node("Declaration-list", parent=parent)

    if get_needed_lookahead() in declaration_firsts:
        declaration(node)
        declaration_list(node)
    elif get_needed_lookahead() in declaration_list_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def declaration(parent):
    node = Node("Declaration", parent=parent)

    if get_needed_lookahead() in declaration_initial_firsts:
        declaration_initial(node)
        declaration_prime(node)
    else:
        random_exception()


def declaration_initial(parent):
    node = Node("Declaration-initial", parent=parent)

    if get_needed_lookahead() in type_specifier_firsts:
        type_specifier(node)
        match("ID", node)
    else:
        random_exception()


def declaration_prime(parent):
    node = Node("Declaration-prime", parent=parent)

    if get_needed_lookahead() in fun_declaration_prime_firsts:
        fun_declaration_prime(node)
    elif get_needed_lookahead() in var_declaration_prime_firsts:
        var_declaration_prime(node)
    else:
        random_exception()


def var_declaration_prime(parent):
    node = Node("Var-declaration-prime", parent=parent)

    if get_needed_lookahead() == ";":
        match(";", node)
    elif get_needed_lookahead() == "[":
        match("[", node)
        match("NUM", node)
        match("]", node)
        match(";", node)
    else:
        random_exception()


def fun_declaration_prime(parent):
    node = Node("Fun-declaration-prime", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        params(node)
        match(")", node)
        compound_stmt(node)
    else:
        random_exception()


def type_specifier(parent):
    node = Node("Type-specifier", parent=parent)

    if get_needed_lookahead() == "int":
        match("int", node)
    elif get_needed_lookahead() == "void":
        match("void", node)
    else:
        random_exception()


def params(parent):
    node = Node("Params", parent=parent)

    if get_needed_lookahead() == "int":
        match("int", node)
        match("ID", node)
        param_prime(node)
        param_list(node)
    elif get_needed_lookahead() == "void":
        match("void", node)


def param_list(parent):
    node = Node("Param-list", parent=parent)

    if get_needed_lookahead() == ",":
        match(",", node)
        param(node)
        param_list(node)
    elif get_needed_lookahead() in param_list_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def param(parent):
    node = Node("Param", parent=parent)

    if get_needed_lookahead() in declaration_initial_firsts:
        declaration_initial(node)
        param_prime(node)
    else:
        random_exception()


def param_prime(parent):
    node = Node("Param-prime", parent=parent)

    if get_needed_lookahead() == "[":
        match("[", node)
        match("]", node)
    elif get_needed_lookahead() in param_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def compound_stmt(parent):
    node = Node("Compound-stmt", parent=parent)

    if get_needed_lookahead() == "{":
        match("{", node)
        declaration_list(node)
        statement_list(node)
        match("}", node)
    else:
        random_exception()


def statement_list(parent):
    node = Node("Statement-list", parent=parent)

    if get_needed_lookahead() in statement_firsts:
        statement(node)
        statement_list(node)
    elif get_needed_lookahead() in statement_list_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def statement(parent):
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
        random_exception()


def expression_stmt(parent):
    node = Node("Expression-stmt", parent=parent)

    if get_needed_lookahead() in expression_firsts:
        expression(node)
        match(";", node)
    elif get_needed_lookahead() == "break":
        match("break", node)
        match(";", node)
    elif get_needed_lookahead() == ";":
        match(";", node)
    else:
        random_exception()


def selection_stmt(parent):
    node = Node("Selection-stmt", parent=parent)

    if get_needed_lookahead() == "if":
        match("if", node)
        match("(", node)
        expression(node)
        match(")", node)
        statement(node)
        else_stmt(node)
    else:
        random_exception()


def else_stmt(parent):
    node = Node("Slse-stmt", parent=parent)

    if get_needed_lookahead() == "endif":
        match("endif", node)
    elif get_needed_lookahead() == "else":
        match("else", node)
        statement(node)
        match("endif", node)
    else:
        random_exception()


def iteration_stmt(parent):
    node = Node("Iteration-stmt", parent=parent)

    if get_needed_lookahead() == "for":
        match("for", node)
        match("(", node)
        expression(node)
        match(";", node)
        expression(node)
        match(";", node)
        expression(node)
        match(")", node)
        statement(node)
    else:
        random_exception()


def return_stmt(parent):
    node = Node("Return-stmt", parent=parent)

    if get_needed_lookahead() == "return":
        match("return", node)
        return_stmt_prime(node)
    else:
        random_exception()


def return_stmt_prime(parent):
    node = Node("Return-stmt-prime", parent=parent)

    if get_needed_lookahead() == ";":
        match(";", node)
    elif get_needed_lookahead() in expression_firsts:
        expression(node)
        match(";", node)
    else:
        random_exception()


def expression(parent):
    node = Node("Expression", parent=parent)

    if get_needed_lookahead() in simple_expression_zegond_firsts:
        simple_expression_zegond(node)
    elif get_needed_lookahead() == "ID":
        match("ID", node)
        b(node)
    else:
        random_exception()


def b(parent):
    node = Node("B", parent=parent)

    if get_needed_lookahead() == "=":
        match("=", node)
        expression(node)
    elif get_needed_lookahead() == "[":
        match("[", node)
        expression(node)
        match("]", node)
        h(node)
    elif get_needed_lookahead() in simple_expression_prime_firsts:
        simple_expression_prime(node)
    else:
        random_exception()


def h(parent):
    node = Node("H", parent=parent)

    if get_needed_lookahead() == "=":
        match("=", node)
        expression(node)
    elif get_needed_lookahead() in g_firsts:
        g(node)
        d(node)
        c(node)
    else:
        random_exception()


def simple_expression_zegond(parent):
    node = Node("Simple-expression-zegond", parent=parent)

    if get_needed_lookahead() in additive_expression_zegond_firsts:
        additive_expression_zegond(node)
        c(node)
    else:
        random_exception()


def simple_expression_prime(parent):
    node = Node("Simple-expression-prime", parent=parent)

    if get_needed_lookahead() in additive_expression_prime_firsts:
        additive_expression_prime(node)
        c(node)
    else:
        random_exception()


def c(parent):
    node = Node("C", parent=parent)

    if get_needed_lookahead() in relop_firsts:
        relop(node)
        additive_expression(node)
    elif get_needed_lookahead() in c_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def relop(parent):
    node = Node("Relop", parent=parent)

    if get_needed_lookahead() == "<":
        match("<", node)
    elif get_needed_lookahead() == "=":
        match("=", node)
    else:
        random_exception()


def additive_expression(parent):
    node = Node("Additive-expression", parent=parent)

    if get_needed_lookahead() in term_firsts:
        term(node)
        d(node)
    else:
        random_exception()


def additive_expression_prime(parent):
    node = Node("Additive-expression-prime", parent=parent)

    if get_needed_lookahead() in term_prime_firsts:
        term_prime(node)
        d(node)
    else:
        random_exception()


def additive_expression_zegond(parent):
    node = Node("Additive-expression-zegond", parent=parent)

    if get_needed_lookahead() in term_zegond_firsts:
        term_zegond(node)
        d(node)
    else:
        random_exception()


def d(parent):
    node = Node("D", parent=parent)

    if get_needed_lookahead() in addop_firsts:
        addop(node)
        term(node)
        d(node)
    elif get_needed_lookahead() in d_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def addop(parent):
    node = Node("Addop", parent=parent)

    if get_needed_lookahead() == "+":
        match("+", node)
    elif get_needed_lookahead() == "-":
        match("-", node)
    else:
        random_exception()


def term(parent):
    node = Node("Term", parent=parent)

    if get_needed_lookahead() in signed_factor_firsts:
        signed_factor(node)
        g(node)
    else:
        random_exception()


def term_prime(parent):
    node = Node("Term-prime", parent=parent)

    if get_needed_lookahead() in signed_factor_prime_firsts:
        signed_factor_prime(node)
        g(node)
    else:
        random_exception()


def term_zegond(parent):
    node = Node("Term-zegond", parent=parent)

    if get_needed_lookahead() in signed_factor_zegond_firsts:
        signed_factor_zegond(node)
        g(node)
    else:
        random_exception()


def g(parent):
    node = Node("G", parent=parent)

    if get_needed_lookahead() == "*":
        match("*", node)
        signed_factor(node)
        g(node)
    elif get_needed_lookahead() in g_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def signed_factor(parent):
    node = Node("Signed-factor", parent=parent)

    if get_needed_lookahead() == "+":
        match("+", node)
        factor(node)
    elif get_needed_lookahead() == "-":
        match("-", node)
        factor(node)
    elif get_needed_lookahead() in factor_firsts:
        factor(node)
    else:
        random_exception()


def signed_factor_prime(parent):
    node = Node("Signed-factor-prime", parent=parent)

    if get_needed_lookahead() in factor_prime_firsts:
        factor_prime(node)
    else:
        random_exception()


def signed_factor_zegond(parent):
    node = Node("Signed-factor-zegond", parent=parent)

    if get_needed_lookahead() == "+":
        match("+", node)
        factor(node)
    elif get_needed_lookahead() == "-":
        match("-", node)
        factor(node)
    elif get_needed_lookahead() in factor_zegond_firsts:
        factor_zegond(node)
    else:
        random_exception()


def factor(parent):
    node = Node("Factor", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        expression(node)
        match(")", node)
    elif get_needed_lookahead() == "ID":
        match("ID", node)
        var_call_prime(node)
    elif get_needed_lookahead() == "NUM":
        match("NUM", node)
    else:
        random_exception()


def var_call_prime(parent):
    node = Node("Var-call-prime", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        args(node)
        match(")", node)
    elif get_needed_lookahead() in var_prime_firsts:
        var_prime(node)
    else:
        random_exception()


def var_prime(parent):
    node = Node("Var-prime", parent=parent)

    if get_needed_lookahead() == "[":
        match("[", node)
        expression(node)
        match("]", node)
    elif get_needed_lookahead() in var_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def factor_prime(parent):
    node = Node("Factor-prime", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        args(node)
        match(")", node)
    elif get_needed_lookahead() in factor_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def factor_zegond(parent):
    node = Node("Factor-zegond", parent=parent)

    if get_needed_lookahead() == "(":
        match("(", node)
        expression(node)
        match(")", node)
    elif get_needed_lookahead() == "NUM":
        match("NUM", node)
    else:
        random_exception()


def args(parent):
    node = Node("Args", parent=parent)

    if get_needed_lookahead() in arg_list_firsts:
        arg_list(node)
    elif get_needed_lookahead() in args_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def arg_list(parent):
    node = Node("Arg-list", parent=parent)

    if get_needed_lookahead() in expression_firsts:
        expression(node)
        arg_list_prime(node)
    else:
        random_exception()


def arg_list_prime(parent):
    node = Node("Arg-list-prime", parent=parent)

    if get_needed_lookahead() == ",":
        match(",", node)
        expression(node)
        arg_list_prime(node)
    elif get_needed_lookahead() in arg_list_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()
