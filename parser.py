from scanner import get_next_token
from firsts import *

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
    if lookahead in declaration_list_firsts:
        deceleration_list()

    else:
        random_exception()


def deceleration_list():
    if lookahead in declaration_firsts:
        declaration()
        deceleration_list()

    else:
        random_exception()


def declaration():
    if lookahead in declaration_initial_firsts:
        declaration_initial()
        declaration_prime()
    else:
        random_exception()


def declaration_initial():
    if lookahead in type_specifier_firsts:
        type_specifier()
        match("ID")
    else:
        random_exception()


def declaration_prime():
    if lookahead in fun_declaration_prime_firsts:
        fun_declaration_prime()
    elif lookahead in var_declaration_prime_firsts:
        var_declaration_prime()
    else:
        random_exception()


def var_declaration_prime():
    if lookahead == ";":
        match(";")
    elif lookahead == "[":
        match("[")
        match("NUM")
        match("]")
        match(";")
    else:
        random_exception()


def fun_declaration_prime():
    if lookahead == "(":
        match("(")
        params()
        match(")")
        compound_stmt()
    else:
        random_exception()


def type_specifier():
    if lookahead == "int":
        match("int")
    elif lookahead == "void":
        match("void")
    else:
        random_exception()


def params():
    if lookahead == "int":
        match("int")
        match("ID")
        param_prime()
        param_list()
    elif lookahead == "void":
        match("void")


def param_list():
    if lookahead == ",":
        match(",")
        param()
        param_list()
    else:
        random_exception()


def param():
    if lookahead in declaration_initial_firsts:
        declaration_initial()
        param_prime()
    else:
        random_exception()


def param_prime():
    if lookahead == "[":
        match("[")
        match("]")
    else:
        random_exception()


def compound_stmt():
    if lookahead == "{":
        match("{")
        deceleration_list()
        statement_list()
        match("}")
    else:
        random_exception()


def statement_list():
    if lookahead in statement_firsts:
        statement()
        statement_list()
    else:
        random_exception()


def statement():
    if lookahead in expression_stmt_firsts:
        expression_stmt()
    elif lookahead in compound_stmt_firsts:
        compound_stmt()
    elif lookahead in selection_stmt_firsts:
        selection_stmt()
    elif lookahead in iteration_stmt_firsts:
        iteration_stmt()
    elif lookahead in return_stmt_firsts:
        return_stmt()
    else:
        random_exception()


def expression_stmt():
    if lookahead in expression_firsts:
        expression()
        match(",")
    elif lookahead == "break":
        match("break")
        match(";")
    elif lookahead == ";":
        match(";")
    else:
        random_exception()


def selection_stmt():
    if lookahead == "if":
        match("if")
        match("(")
        expression()
        match(")")
        statement()
        else_stmt()
    else:
        random_exception()


def else_stmt():
    if lookahead == "endif":
        match("endif")
    elif lookahead == "else":
        match("else")
        statement()
        match("endif")
    else:
        random_exception()


def iteration_stmt():
    if lookahead == "for":
        match("for")
        match("(")
        expression()
        match(";")
        expression()
        match(";")
        expression()
        match(")")
        statement()
    else:
        random_exception()


def return_stmt():
    if lookahead == "return":
        match("return")
        return_stmt_prime()
    else:
        random_exception()


def return_stmt_prime():
    if lookahead == ";":
        match(";")
    elif lookahead in expression_firsts:
        expression()
        match(";")
    else:
        random_exception()


def expression():
    if lookahead in simple_expression_zegond_firsts:
        simple_expression_zegond()
    elif lookahead == "ID":
        match("ID")
        b()
    else:
        random_exception()


def b():
    if lookahead in expression_firsts:
        expression()
    elif lookahead == "[":
        match("[")
        expression()
        match("]")
        h()
    elif lookahead in simple_expression_prime_firsts:
        simple_expression_prime()
    else:
        random_exception()


def h():
    if lookahead in expression_firsts:
        expression()
    elif lookahead in g_firsts:
        g()
        d()
        c()
    else:
        random_exception()


def simple_expression_zegond():
    if lookahead in additive_expression_zegond_firsts:
        additive_expression_zegond()
        c()
    else:
        random_exception()


def simple_expression_prime():
    if lookahead in additive_expression_prime_firsts:
        additive_expression_prime()
        c()
    else:
        random_exception()


def c():
    if lookahead in relop_firsts:
        relop()
        additive_expression()
    else:
        random_exception()


def relop():
    if lookahead == "<":
        match("<")
    elif lookahead == "=":
        match("=")
    else:
        random_exception()


def additive_expression():
    if lookahead in term_firsts:
        term()
        d()
    else:
        random_exception()


def additive_expression_prime():
    if lookahead in term_prime_firsts:
        term_prime()
        d()
    else:
        random_exception()


def additive_expression_zegond():
    if lookahead in term_zegond_firsts:
        term_zegond()
        d()
    else:
        random_exception()


def d():
    if lookahead in addop_firsts:
        addop()
        term()
        d()
    else:
        random_exception()


def addop():
    if lookahead == "+":
        match("+")
    elif lookahead == "-":
        match("-")
    else:
        random_exception()


def term():
    if lookahead in signed_factor_firsts:
        signed_factor()
        g()
    else:
        random_exception()


def term_prime():
    if lookahead in signed_factor_prime_firsts:
        simple_expression_prime()
        g()
    else:
        random_exception()


def term_zegond():
    if lookahead in signed_factor_zegond_firsts:
        simple_expression_zegond()
        g()
    else:
        random_exception()


def g():
    if lookahead == "*":
        match("*")
        signed_factor()
        g()
    else:
        random_exception()


def signed_factor():
    if lookahead == "+":
        match("+")
        factor()
    elif lookahead == "-":
        match("-")
        factor()
    elif lookahead in factor_firsts:
        factor()
    else:
        random_exception()


def signed_factor_prime():
    if lookahead in factor_prime_firsts:
        factor_prime()
    else:
        random_exception()


def signed_factor_zegond():
    if lookahead == "+":
        match("+")
        factor()
    elif lookahead == "-":
        match("-")
        factor()
    elif lookahead in factor_firsts:
        factor_zegond()
    else:
        random_exception()


def factor():
    if lookahead == "(":
        match("(")
        expression()
        match(")")
    elif lookahead == "ID":
        match("ID")
        var_call_prime()
    elif lookahead == "NUM":
        match("NUM")
    else:
        random_exception()


def var_call_prime():
    if lookahead == "(":
        match("(")
        args()
        match(")")
    elif lookahead in var_prime_firsts:
        var_prime()
    else:
        random_exception()


def var_prime():
    if lookahead == match("["):
        match("[")
        expression()
        match("]")
    else:
        random_exception()


def factor_prime():
    if lookahead == "(":
        match("(")
        args()
        match(")")
    else:
        random_exception()


def factor_zegond():
    if lookahead == "(":
        match("(")
        expression()
        match(")")
    elif lookahead == "NUM":
        match("NUM")
    else:
        random_exception()


def args():
    if lookahead in arg_list_firsts:
        arg_list()
    else:
        random_exception()


def arg_list():
    if lookahead in expression_firsts:
        expression()
        arg_list_prime()
    else:
        random_exception()


def arg_list_prime():
    if lookahead == ",":
        match(",")
        expression()
        arg_list_prime()
    else:
        random_exception()
