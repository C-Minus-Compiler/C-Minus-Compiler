from utils.token import TokenType


class Scanner:
    INPUT = "input.txt"
    code = open(INPUT, 'r')
    line = 0
    char = 0
    read_chars = 0 # refers to chars read by far

class DFA:
    pass


# returns: TokenType, lexeme, line_number
# return empty tuple for EOF
def get_next_token():
    return TokenType.ID, "dutchman", 0  
