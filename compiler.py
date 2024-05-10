from utils.lexical_errors import LexicalError
from parser import initial_parser


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
    initial_parser()


if __name__ == "__main__":
    main()
