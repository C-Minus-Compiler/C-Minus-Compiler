from anytree import Node
from scanner import get_next_token
from firsts import *
from follows import *

lookahead = ""


def random_exception():
    raise Exception("Random Exception")


def match(expected_token):
    global lookahead
    if expected_token == lookahead:
        lookahead = get_next_token()
    else:
        random_exception()


def initial_parser():
    global lookahead
    lookahead = get_next_token()
    program()


def program():
    node = Node("Program")

    if lookahead in declaration_list_firsts:
        deceleration_list(node)

    else:
        random_exception()


def deceleration_list(parent):
    node = Node("Deceleration-list", parent=parent)

    if lookahead in declaration_firsts:
        declaration(node)
        deceleration_list(node)
    elif lookahead in declaration_list_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def declaration(parent):
    node = Node("Deceleration", parent=parent)

    if lookahead in declaration_initial_firsts:
        declaration_initial(node)
        declaration_prime(node)
    else:
        random_exception()


def declaration_initial(parent):
    node = Node("Declaration-initial", parent=parent)

    if lookahead in type_specifier_firsts:
        type_specifier(node)
        match("ID")
    else:
        random_exception()


def declaration_prime(parent):
    node = Node("Declaration-prime", parent=parent)

    if lookahead in fun_declaration_prime_firsts:
        fun_declaration_prime(node)
    elif lookahead in var_declaration_prime_firsts:
        var_declaration_prime(node)
    else:
        random_exception()


def var_declaration_prime(parent):
    node = Node("Var_declaration-prime", parent=parent)

    if lookahead == ";":
        match(";")
    elif lookahead == "[":
        match("[")
        match("NUM")
        match("]")
        match(";")
    else:
        random_exception()


def fun_declaration_prime(parent):
    node = Node("fun_declaration-prime", parent=parent)

    if lookahead == "(":
        match("(")
        params(node)
        match(")")
        compound_stmt(node)
    else:
        random_exception()


def type_specifier(parent):
    node = Node("Type-specifier", parent=parent)

    if lookahead == "int":
        match("int")
    elif lookahead == "void":
        match("void")
    else:
        random_exception()


def params(parent):
    node = Node("Params", parent=parent)

    if lookahead == "int":
        match("int")
        match("ID")
        param_prime(node)
        param_list(node)
    elif lookahead == "void":
        match("void")


def param_list(parent):
    node = Node("Param-list", parent=parent)

    if lookahead == ",":
        match(",")
        param(node)
        param_list(node)
    elif lookahead in param_list_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def param(parent):
    node = Node("Param", parent=parent)

    if lookahead in declaration_initial_firsts:
        declaration_initial(node)
        param_prime(node)
    else:
        random_exception()


def param_prime(parent):
    node = Node("Param-prime", parent=parent)

    if lookahead == "[":
        match("[")
        match("]")
    elif lookahead in param_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def compound_stmt(parent):
    node = Node("Compound-stmt", parent=parent)

    if lookahead == "{":
        match("{")
        deceleration_list(node)
        statement_list(node)
        match("}")
    else:
        random_exception()


def statement_list(parent):
    node = Node("Statement-list", parent=parent)

    if lookahead in statement_firsts:
        statement(node)
        statement_list(node)
    elif lookahead in statement_list_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def statement(parent):
    node = Node("Statement", parent=parent)

    if lookahead in expression_stmt_firsts:
        expression_stmt(node)
    elif lookahead in compound_stmt_firsts:
        compound_stmt(node)
    elif lookahead in selection_stmt_firsts:
        selection_stmt(node)
    elif lookahead in iteration_stmt_firsts:
        iteration_stmt(node)
    elif lookahead in return_stmt_firsts:
        return_stmt(node)
    else:
        random_exception()


def expression_stmt(parent):
    node = Node("Expression-stmt", parent=parent)

    if lookahead in expression_firsts:
        expression(node)
        match(",")
    elif lookahead == "break":
        match("break")
        match(";")
    elif lookahead == ";":
        match(";")
    else:
        random_exception()


def selection_stmt(parent):
    node = Node("Selection-stmt", parent=parent)

    if lookahead == "if":
        match("if")
        match("(")
        expression(node)
        match(")")
        statement(node)
        else_stmt(node)
    else:
        random_exception()


def else_stmt(parent):
    node = Node("Slse-stmt", parent=parent)

    if lookahead == "endif":
        match("endif")
    elif lookahead == "else":
        match("else")
        statement(node)
        match("endif")
    else:
        random_exception()


def iteration_stmt(parent):
    node = Node("Iteration-stmt", parent=parent)

    if lookahead == "for":
        match("for")
        match("(")
        expression(node)
        match(";")
        expression(node)
        match(";")
        expression(node)
        match(")")
        statement(node)
    else:
        random_exception()


def return_stmt(parent):
    node = Node("Return-stmt", parent=parent)

    if lookahead == "return":
        match("return")
        return_stmt_prime(node)
    else:
        random_exception()


def return_stmt_prime(parent):
    node = Node("Return-stmt-prime", parent=parent)

    if lookahead == ";":
        match(";")
    elif lookahead in expression_firsts:
        expression(node)
        match(";")
    else:
        random_exception()


def expression(parent):
    node = Node("Expression", parent=parent)

    if lookahead in simple_expression_zegond_firsts:
        simple_expression_zegond(node)
    elif lookahead == "ID":
        match("ID")
        b(node)
    else:
        random_exception()


def b(parent):
    node = Node("B", parent=parent)

    if lookahead in expression_firsts:
        expression(node)
    elif lookahead == "[":
        match("[")
        expression(node)
        match("]")
        h(node)
    elif lookahead in simple_expression_prime_firsts:
        simple_expression_prime(node)
    else:
        random_exception()


def h(parent):
    node = Node("H", parent=parent)

    if lookahead in expression_firsts:
        expression(node)
    elif lookahead in g_firsts:
        g(node)
        d(node)
        c(node)
    else:
        random_exception()


def simple_expression_zegond(parent):
    node = Node("Simple-expression-zegond", parent=parent)

    if lookahead in additive_expression_zegond_firsts:
        additive_expression_zegond(node)
        c(node)
    else:
        random_exception()


def simple_expression_prime(parent):
    node = Node("Simple-expression-prime", parent=parent)

    if lookahead in additive_expression_prime_firsts:
        additive_expression_prime(node)
        c(node)
    else:
        random_exception()


def c(parent):
    node = Node("C", parent=parent)

    if lookahead in relop_firsts:
        relop(node)
        additive_expression(node)
    elif lookahead in c_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def relop(parent):
    node = Node("Relop", parent=parent)

    if lookahead == "<":
        match("<")
    elif lookahead == "=":
        match("=")
    else:
        random_exception()


def additive_expression(parent):
    node = Node("Additive-expression", parent=parent)

    if lookahead in term_firsts:
        term(node)
        d(node)
    else:
        random_exception()


def additive_expression_prime(parent):
    node = Node("Additive-expression-prime", parent=parent)

    if lookahead in term_prime_firsts:
        term_prime(node)
        d(node)
    else:
        random_exception()


def additive_expression_zegond(parent):
    node = Node("Additive-expression-zegond", parent=parent)

    if lookahead in term_zegond_firsts:
        term_zegond(node)
        d(node)
    else:
        random_exception()


def d(parent):
    node = Node("D", parent=parent)

    if lookahead in addop_firsts:
        addop(node)
        term(node)
        d(node)
    elif lookahead in d_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def addop(parent):
    node = Node("Addop", parent=parent)

    if lookahead == "+":
        match("+")
    elif lookahead == "-":
        match("-")
    else:
        random_exception()


def term(parent):
    node = Node("Term", parent=parent)

    if lookahead in signed_factor_firsts:
        signed_factor(node)
        g(node)
    else:
        random_exception()


def term_prime(parent):
    node = Node("Term-prime", parent=parent)

    if lookahead in signed_factor_prime_firsts:
        simple_expression_prime(node)
        g(node)
    else:
        random_exception()


def term_zegond(parent):
    node = Node("Term-zegond", parent=parent)

    if lookahead in signed_factor_zegond_firsts:
        simple_expression_zegond(node)
        g(node)
    else:
        random_exception()


def g(parent):
    node = Node("G", parent=parent)

    if lookahead == "*":
        match("*")
        signed_factor(node)
        g(node)
    elif lookahead in g_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def signed_factor(parent):
    node = Node("Signed-factor", parent=parent)

    if lookahead == "+":
        match("+")
        factor(node)
    elif lookahead == "-":
        match("-")
        factor(node)
    elif lookahead in factor_firsts:
        factor(node)
    else:
        random_exception()


def signed_factor_prime(parent):
    node = Node("Signed-factor-prime", parent=parent)

    if lookahead in factor_prime_firsts:
        factor_prime(node)
    else:
        random_exception()


def signed_factor_zegond(parent):
    node = Node("Signed-factor-zegond", parent=parent)

    if lookahead == "+":
        match("+")
        factor(node)
    elif lookahead == "-":
        match("-")
        factor(node)
    elif lookahead in factor_firsts:
        factor_zegond(node)
    else:
        random_exception()


def factor(parent):
    node = Node("Factor", parent=parent)

    if lookahead == "(":
        match("(")
        expression(node)
        match(")")
    elif lookahead == "ID":
        match("ID")
        var_call_prime(node)
    elif lookahead == "NUM":
        match("NUM")
    else:
        random_exception()


def var_call_prime(parent):
    node = Node("Var-call-prime", parent=parent)

    if lookahead == "(":
        match("(")
        args(node)
        match(")")
    elif lookahead in var_prime_firsts:
        var_prime(node)
    else:
        random_exception()


def var_prime(parent):
    node = Node("Var-prime", parent=parent)

    if lookahead == match("["):
        match("[")
        expression(node)
        match("]")
    elif lookahead in var_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def factor_prime(parent):
    node = Node("Factor-prime", parent=parent)

    if lookahead == "(":
        match("(")
        args(node)
        match(")")
    elif lookahead in factor_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def factor_zegond(parent):
    node = Node("Factor-zegond", parent=parent)

    if lookahead == "(":
        match("(")
        expression(node)
        match(")")
    elif lookahead == "NUM":
        match("NUM")
    else:
        random_exception()


def args(parent):
    node = Node("Args", parent=parent)

    if lookahead in arg_list_firsts:
        arg_list(node)
    elif lookahead in args_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()


def arg_list(parent):
    node = Node("Arg-list", parent=parent)

    if lookahead in expression_firsts:
        expression(node)
        arg_list_prime(node)
    else:
        random_exception()


def arg_list_prime(parent):
    node = Node("Arg-list-prime", parent=parent)

    if lookahead == ",":
        match(",")
        expression(node)
        arg_list_prime(node)
    elif lookahead in arg_list_prime_follows:
        Node("epsilon", parent=node)
    else:
        random_exception()
