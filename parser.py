from scanner import get_next_token
from firsts import *

lookahead = ""


def match(expected_token):
    global lookahead
    if expected_token == lookahead:
        lookahead = get_next_token()
    else:
        raise Exception("Random Exception")


def program():
    global lookahead
    if lookahead in declaration_list_firsts:
        deceleration_list()


def deceleration_list():
    pass


def declaration():
    pass


def declaration_initial():
    pass


def declaration_prime():
    pass


def var_declaration_prime():
    pass


def fun_declaration_prime():
    pass


def type_specifier():
    pass


def params():
    pass


def param_list():
    pass


def param():
    pass


def param_prime():
    pass


def compound_stmt():
    pass


def statement_list():
    pass


def statement():
    pass


def expression_stmt():
    pass


def selection_stmt():
    pass


def else_stmt():
    pass


def iteration_stmt():
    pass


def return_stmt():
    pass


def return_stmt_prime():
    pass


def expression():
    pass


def b():
    pass


def h():
    pass


def simple_expression_zegond():
    pass


def simple_expression_prime():
    pass


def c():
    pass


def relop():
    pass


def additive_expression():
    pass


def additive_expression_prime():
    pass


def additive_expression_zegond():
    pass


def d():
    pass


def addop():
    pass


def term():
    pass


def term_prime():
    pass


def term_zegond():
    pass


def g():
    pass


def signed_factor():
    pass


def signed_factor_prime():
    pass


def signed_factor_zegond():
    pass


def factor():
    pass


def var_call_prime():
    pass


def var_prime():
    pass


def factor_prime():
    pass


def factor_zegond():
    pass


def args():
    pass


def arg_list():
    pass


def arg_list_prime():
    pass
