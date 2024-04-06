from scanner import get_next_token
from utils.token import TokenType



def print_line_tokens(file, line_buffer):
    line = ""
    for token in line_buffer:
        line += f"({token[0]}, {token[1]}) "
    line += "\n"
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
    line_buffer = []
    last_line = 0
    
    dummy_counter = 0

    while last_token:
        last_token = get_next_token()
        if last_line != last_token[2]:
            print_line_tokens(tokens, line_buffer)
            last_line = last_token[1]
            line_buffer = []

        if (last_token[0] != TokenType.WHITESPACE and last_token[0] != TokenType.COMMENT):
            line_buffer.append(last_token)
        
        # TODO: Remove the following
        dummy_counter += 1
        if dummy_counter > 10:
            break
        
    print_line_tokens(tokens, line_buffer)

    symbol_table.close()
    lexical_errors.close() 
    tokens.close()
    code.close()

if __name__ == "__main__":
    main()
