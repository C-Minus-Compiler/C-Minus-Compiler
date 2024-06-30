# AmirMahdi Koushehi
# Mohsen Ghasemi
import os

from scanner import Scanner
from utils.lexical_errors import LexicalError
from parser import initial_parser
from anytree import RenderTree
from codegen import CodeGenerator


def print_line_tokens(line_number, file, line_buffer):
    if len(line_buffer) == 0:
        return
    line = f"{line_number}.".ljust(4)
    for token in line_buffer:
        line += f"({token[0].value}, {token[1]}) "
    line += "\n"
    file.write(line)


def print_line_lexical_errors(line_number, file, line_buffer):
    if len(line_buffer) == 0:
        return
    line = f"{line_number}.".ljust(4)
    for error in line_buffer:
        lexeme = error[1]
        if error[0] == LexicalError.UNCLOSED_COMMENT:
            lexeme = "/*comme..."
        line += f"({lexeme}, {error[0].value}) "
    line += "\n"
    file.write(line)


def print_symbol_table(file, symbols):
    for i, s in enumerate(symbols):
        line = f"{i + 1}.".ljust(4)
        line += s
        line += '\n'
        file.write(line)


def main():
    complete_tree, parser_errors, cg = initial_parser()

    semantic_errors_file = open("semantic_errors.txt", "w")
    semantic_errors_msgs = ""
    if len(cg.semantic_errors):
        for i in cg.semantic_errors:
            semantic_errors_msgs += f"{i}\n"
    else:
        semantic_errors_msgs += "The input program is semantically correct."
    semantic_errors_file.write(semantic_errors_msgs)
    semantic_errors_file.close()
    code_generator_output_file = open("output.txt", "w")
    final_output = ""
    if not len(cg.semantic_errors):
        for i, j in enumerate(cg.program_block.blocks):
            # print(f"{i}{j}")
            final_output += f"{i}{j}\n"
    else:
        final_output += "The code has not been generated."
    code_generator_output_file.write(final_output)
    code_generator_output_file.close()
    syntax_errors_file = open("syntax_errors.txt", "w")
    if parser_errors:
        syntax_errors_file.write("\n".join(parser_errors))
    else:
        syntax_errors_file.write("There is no syntax error.")
    syntax_errors_file.close()

    parser_tree_file = open("parse_tree.txt", "w")
    tree = ""
    for pre, fill, node in RenderTree(complete_tree):
        # print("%s%s" % (pre, node.name))
        tree += "%s%s" % (pre, node.name) + "\n"
    parser_tree_file.write(tree)
    parser_tree_file.close()


if __name__ == "__main__":
    main()
