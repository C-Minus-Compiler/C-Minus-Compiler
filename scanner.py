import re

from utils.token import TokenType, TokenRegex


class Scanner:
    def __init__(self, input_code):
        self.code = input_code
        self.line = 1
        self.char = 0
        self.read_chars = 0  # refers to chars read by far
        self.dfa = DFA()
        self.current_state = "start_state"
        self.current_token = ""
        self.tokens = []

    def read_next_index_of_code(self):
        char = self.code[self.char]
        self.char += 1
        return char

    def print_line_tokens(self, line_buffer):
        if not line_buffer:
            return
        line = ""
        print(f"{self.line}.	", end="")
        for token in line_buffer:
            line += f"({token[0].name}, {token[1]}) "
        print(line)

    def is_token_keyword(self, token):
        if token in ["if", "else", "void", "int", "for", "break", "return", "endif"]:
            return True
        return False

    # returns: TokenType, lexeme, line_number
    # return empty tuple for EOF
    def get_next_token(self):
        self.char = self.read_chars
        while True:
            char = self.read_next_index_of_code()
            next_state = self.dfa.next_state(self.current_state, char)

            if self.current_state == "start_state":
                self.current_token += char
                self.current_state = next_state
            elif self.current_state == next_state:
                self.current_token += char
            else:
                self.char -= 1
                if (self.current_state == 'number_state' or self.current_state == 'identifier_state' or
                        self.current_state == 'symbol_state'):

                    token_type = ""
                    match self.current_state:
                        case "number_state":
                            token_type = TokenType.NUM
                        case "symbol_state":
                            token_type = TokenType.SYMBOL
                        case "identifier_state":
                            if self.is_token_keyword(self.current_token):
                                token_type = TokenType.KEYWORD
                            else:
                                token_type = TokenType.ID

                    token_tuple = (token_type, self.current_token)
                    self.tokens.append(token_tuple)

                    self.read_chars = self.char
                    self.current_state = "start_state"
                    self.current_token = ""
                    break

                self.current_state = "start_state"
                self.current_token = ''
                continue

            if char == "\n":
                self.print_line_tokens(self.tokens)
                self.line += 1
                self.tokens = []


# class DFA:
#     start = 0
#     current_state = 0
#     states = (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
#     accept_states = (2, 4, 5, 7, 8, 11, 14, 15)
#     stared_states = (2, 4, 8)
#
#     # (state, "regex", "true means should be false means should not be", "next_state")
#     transitions = ((0, r'[0-9]', True, 1),
#                    (1, r'[0-9]', False, 2),
#                    (0, r'[a-zA-Z]', True, 3),
#                    (3, r'[a-zA-Z0-9]', True, 3),
#                    (3, r'[a-zA-Z0-9]', False, 4),
#                    (0, r';|:|,|\[|\]|\(|\)|\{|\}|\+|\-|\*|<', True, 5),
#                    (0, r'=', True, 6),
#                    (6, r'=', True, 7),
#                    (6, r'=', False, 8),
#                    (0, r'/', True, 9),
#                    (9, r'\*', True, 12),
#                    (12, r'\*', False, 12),
#                    (12, r'\*', True, 13),
#                    (13, r'\*|/', False, 12),
#                    (13, r'\*', True, 13),
#                    (13, r'/', True, 14),
#                    (0, r' |\n|\r|\t|\v|\f', True, 15))
#
#     # returns true if there is a valid next state
#     def next_state(self, c):
#         # for trn in self.transitions:
#         #     if self.current_state == trn[0] and (trn[2] if re.match(trn[1], c) != None else not trn[2]):
#         #         self.current_state = trn[2]
#         #         return True
#         # return False
#         pass
#
#     # returns: Bool, Bool (accept, stared)
#     def accept(self):
#         return self.current_state in self.accept_states, self.current_state in self.stared_states

def is_number_regex(char):
    return re.match('[0-9]', char)


def is_letters_regex(char):
    return re.match('[a-zA-Z]', char)


def is_symbol_regex(char):
    return re.match(';|:|\[|]|\(|\)|{|}|\+|-|\*|=|<|,', char)


def is_whitespace_regex(char):
    return re.match(" |\n|\r|\t|\v|\f", char)


class DFA:
    # states are: number, identifier, symbol, whitespaces
    def next_state(self, current_state, char):
        match current_state:
            # from initial state, we can go to every states
            case "start_state":
                if is_number_regex(char):
                    return "number_state"
                if is_letters_regex(char):
                    return "identifier_state"
                if is_symbol_regex(char):
                    return "symbol_state"
                if is_whitespace_regex(char):
                    return "whitespace_state"
            case "number_state":
                if is_number_regex(char):
                    return "number_state"
                if is_symbol_regex(char):
                    return "symbol_state"
                if is_whitespace_regex(char):
                    return "whitespace_state"
            case "identifier_state":
                if is_number_regex(char) or is_letters_regex(char):
                    return "identifier_state"
                if is_symbol_regex(char):
                    return "symbol_state"
                if is_whitespace_regex(char):
                    return "whitespace_state"
            case "symbol_state":
                if is_number_regex(char):
                    return "number_state"
                if is_letters_regex(char):
                    return "identifier_state"
                if is_symbol_regex(char):
                    return "start_state"
                if is_whitespace_regex(char):
                    return "whitespace_state"
            case "whitespace_state":
                if is_number_regex(char):
                    return "number_state"
                if is_letters_regex(char):
                    return "identifier_state"
                if is_symbol_regex(char):
                    return "symbol_state"
                if is_whitespace_regex(char):
                    return "whitespace_state"


def run(input_code):
    scanner = Scanner(input_code=input_code)
    while True:
        scanner.get_next_token()
