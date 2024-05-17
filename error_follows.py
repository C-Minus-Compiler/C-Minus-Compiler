program_error_follows = ["ID", ";", "[", "NUM", "]", "(", ")", ",", "{", "}", "break", "if", "endif", "else", "for",
                         "return", "=", "<", "==", "+", "-", "*"]
declaration_list_error_follows = ["[", "]", ")", ",", "endif", "else", "=", "<", "==", "*"]
declaration_error_follows = ["ID", ";", "NUM", "(", "{", "}", "break", "if", "for", "return", "+", "-", "$"]
declaration_initial_error_follows = [";", "[", "(", ")", ","]  # ok
declaration_prime_error_follows = ["ID", "NUM", "int", "void", "{", "}", "break", "if", "for", "return", "+", "-", "$"]
var_declaration_prime_error_follows = ["ID", "NUM", "(", "int", "void", "{", "}", "break", "if", "for", "return",
                                       "+", "-", "$"]
fun_declaration_prime_error_follows = ["ID", ";", "NUM", "int", "void", "{", "}", "break", "if", "for", "return", "+",
                                       "-", "$"]
type_specifier_error_follows = ["ID"]  # ok
params_error_follows = [")"]  # ok
param_list_error_follows = ["ID", ";", "[", "NUM", "]", "(", "int", "void", "{", "}", "break", "if", "endif", "else",
                            "for", "return", "=", "<", "==", "+", "-", "*", "$"]
param_error_follows = [")", ","]  # ok
param_prime_error_follows = ["ID", ";", "NUM", "]", "(", "int", "void", "{", "}", "break", "if", "endif", "else", "for",
                             "return", "=", "<", "==", "+", "-", "*", "$"]
compound_stmt_error_follows = ["ID", ";", "NUM", "(", "int", "void", "}", "break", "if", "endif", "else", "for",
                               "return", "+", "-", "$"]
statement_list_error_follows = ["[", "]", ")", "int", "void", ",", "endif", "else", "=", "<", "==", "*", "$"]
statement_error_follows = ["}", "endif", "else"]
expression_stmt_error_follows = ["{", "}", "if", "endif", "else", "for", "return"]
selection_stmt_error_follows = ["ID", ";", "NUM", "(", "{", "}", "break", "endif", "else", "for", "return", "+", "-"]
else_stmt_error_follows = ["ID", ";", "NUM", "(", "{", "}", "break", "if", "for", "return", "+", "-"]
iteration_stmt_error_follows = ["ID", ";", "NUM", "(", "{", "}", "break", "if", "endif", "else", "for", "return", "+",
                                "-"]  # ok
return_stmt_error_follows = ["ID", ";", "NUM", "(", "{", "}", "break", "if", "endif", "else", "for", "+", "-"]
return_stmt_prime_error_follows = ["{", "}", "break", "if", "endif", "else", "for", "return"]
expression_error_follows = [";", "]", ")", ","]  # ok
b_error_follows = ["ID", "NUM", "int", "void", "{", "}", "break", "if", "endif", "else", "for", "return", "$"]
h_error_follows = ["$", "ID", "[", "NUM", "(", "int", "void", "{", "}", "break", "if", "endif", "else", "for", "return"]
simple_expression_zegond_error_follows = [";", "]", ")", ","]  # ok
simple_expression_prime_error_follows = ["ID", "[", "NUM", "int", "void", "{", "}", "break", "if", "endif", "else",
                                         "for", "return", "=", "$"]
c_error_follows = ["ID", "[", "NUM", "(", "int", "void", "{", "}", "break", "if", "endif", "else", "for", "return",
                   "=", "+", "-", "*", "$"]
relop_error_follows = ["ID", "NUM", "(", "+", "-"]  # ok
additive_expression_error_follows = [";", "]", ")", ","]  # ok
additive_expression_prime_error_follows = ["ID", "[", "NUM", "int", "void", "{", "}", "break", "if", "endif",
                                           "else", "for", "return", "=", "$"]
additive_expression_zegond_error_follows = [";", "]", ")", ",", "<", "=="]  # ok
d_error_follows = ["ID", "[", "NUM", "(", "int", "void", "{", "}", "break", "if", "endif", "else", "for", "return",
                   "=", "*", "$"]
addop_error_follows = ["ID", "NUM", "(", ]
term_error_follows = [";", "]", ")", ",", "<", "=="]
term_prime_error_follows = ["ID", "[", "NUM", "int", "void", "{", "}", "break", "if", "endif", "else", "for",
                            "return", "=", "$"]
term_zegond_error_follows = [";", "]", ")", ",", "<", "=="]
g_error_follows = ["ID", "[", "NUM", "(", "int", "void", "{", "}", "break", "if", "endif", "else", "for", "return",
                   "=", "$"]
signed_factor_error_follows = [";", "]", ")", ",", "<", "==", "*"]
signed_factor_prime_error_follows = ["ID", "[", "NUM", "int", "void", "{", "}", "break", "if", "endif", "else",
                                     "for", "return", "=", "$"]
signed_factor_zegond_error_follows = [";", "]", ")", ",", "<", "==", "*"]
factor_error_follows = [";", "]", ")", ",", "<", "==", "+", "-", "*"]  # ok
var_call_prime_error_follows = ["ID", "NUM", "int", "void", "{", "}", "break", "if", "endif", "else", "for",
                                "return", "=", "$"]
var_prime_error_follows = ["ID", "NUM", "(", "int", "void", "{", "}", "break", "if", "endif", "else", "for",
                           "return", "=", "$"]
factor_prime_error_follows = ["ID", "[", "NUM", "int", "void", "{", "}", "break", "if", "endif", "else", "for",
                              "return", "=", "$"]
factor_zegond_error_follows = [";", "]", ")", ",", "<", "==", "+", "-", "*"]  # ok
args_error_follows = [";", "[", "]", "int", "void", ",", "{", "}", "break", "if", "endif", "else", "for", "return",
                      "=", "<", "==", "*", "$"]
arg_list_error_follows = [")"]  # ok
arg_list_prime_error_follows = ["ID", ";", "[", "NUM", "]", "(", "int", "void", "{", "}", "break", "if", "endif",
                                "else", "for", "return", "=", "<", "==", "+", "-", "*", "$"]
