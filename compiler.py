from scanner import Scanner, get_next_token
from utils.lexical_errors import LexicalError
from utils.token import TokenType


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
    INPUT = "input.txt"
    code = open(INPUT, "r")

    TOKENS = "tokens.txt"
    tokens = open(TOKENS, "w")

    LEXICAL_ERRORS = "lexical_errors.txt"
    lexical_errors = open(LEXICAL_ERRORS, "w")

    SYMBOL_TABLE = "symbol_table.txt"
    symbol_table = open(SYMBOL_TABLE, "w")

    last_token = (TokenType.COMMENT, "", 0)
    token_line_buffer = []
    lexical_errors_buffer = []

    last_line = 1
    has_lexical_error = False

    while last_token:
        last_token = get_next_token()

        if len(last_token) == 0:
            break

        if last_line != last_token[2]:
            print_line_tokens(last_line, tokens, token_line_buffer)
            print_line_lexical_errors(last_line, lexical_errors, lexical_errors_buffer)
            last_line = last_token[2]
            token_line_buffer = []
            lexical_errors_buffer = []

        if isinstance(last_token[0], TokenType) and (last_token[0] != TokenType.WHITESPACE and
                                                     last_token[0] != TokenType.COMMENT):
            token_line_buffer.append(last_token)
        elif isinstance(last_token[0], LexicalError):
            has_lexical_error = True
            lexical_errors_buffer.append(last_token)

    print_line_tokens(last_line, tokens, token_line_buffer)
    print_line_lexical_errors(last_line, lexical_errors, lexical_errors_buffer)
    if not has_lexical_error:
        lexical_errors.write("There is no lexical error.\n")

    print_symbol_table(symbol_table, Scanner.symbols)

    symbol_table.close()
    lexical_errors.close()
    tokens.close()
    code.close()


if __name__ == "__main__":
    main()
