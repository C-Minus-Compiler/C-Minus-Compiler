import re

from utils.token import TokenType
from utils.lexical_errors import LexicalError


class Scanner:
    INPUT = "input.txt"
    file = open(INPUT, 'r', newline='')
    line = 1
    buffered_new_lines = 0
    read_chars = 0  # refers to chars read by far
    symbols = {"if", "else", "void", "int", "for", "break", "return", "endif"}


class DFA:
    KEYWORDS = ("if", "else", "void", "int", "for", "break", "return", "endif")
    start = 0
    current_state = 0
    states = (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    accept_states = (2, 4, 5, 7, 8, 11, 14, 15)
    stared_states = (2, 4, 8)

    # (state, "regex", "true means should be false means should not be", "next_state")
    transitions = ((0, r'[0-9]', True, 1),
                   (1, r'[0-9]', True, 1),
                   (1, r'[0-9a-zA-Z]', False, 2),
                   (0, r'[a-zA-Z]', True, 3),
                   (3, r'[a-zA-Z0-9]', True, 3),
                   (3, r'[a-zA-Z0-9]', False, 4),
                   (0, r';|:|,|\[|\]|\(|\)|\{|\}|\+|\-|\*|<', True, 5),
                   (0, r'=', True, 6),
                   (6, r'=', True, 7),
                   (6, r'=', False, 8),
                   (0, r'/', True, 9),
                   (9, r'\*', True, 12),
                   (12, r'\*', False, 12),
                   (12, r'\*', True, 13),
                   (13, r'\*|/', False, 12),
                   (13, r'\*', True, 13),
                   (13, r'/', True, 14),
                   (0, r' |\n|\r|\t|\v|\f', True, 15))

    # returns true if there is a valid next state
    def next_state(self, c):
        is_invalid = False
        if re.match(r'[a-zA-Z0-9]|;|:|,|\[|\]|\(|\)|\{|\}|\+|\-|\*|<|/|\\|\n|\r|\t|\v|\f|=| ', c) == None:
            is_invalid = True
        if is_invalid and self.current_state == 12:
            return True
        elif is_invalid and self.current_state == 13:
            self.current_state = 12
            return True
        elif is_invalid:
            return False

        for trn in self.transitions:
            if self.current_state == trn[0] and (trn[2] if re.match(trn[1], c) != None else not trn[2]):
                self.current_state = trn[3]
                return True
        return False

    # returns: Bool, Bool (accept, stared)
    def accept(self):
        return self.current_state in self.accept_states, self.current_state in self.stared_states

    def get_accept_state_token_type(self, lexeme):
        if self.current_state == 2:
            return TokenType.NUM
        elif self.current_state == 4 and lexeme in self.KEYWORDS:
            return TokenType.KEYWORD
        elif self.current_state == 4:
            return TokenType.ID
        elif self.current_state in (5, 7, 8):
            return TokenType.SYMBOL
        elif self.current_state == 14:
            return TokenType.COMMENT
        elif self.current_state == 15:
            return TokenType.WHITESPACE
        return None

    def get_state_lexical_error(self):
        if self.current_state == 1:
            return LexicalError.INVALID_NUMBER
        elif self.current_state in (12, 13):
            return LexicalError.UNCLOSED_COMMENT
        return LexicalError.INVALID_INPUT


# returns: TokenType, lexeme, line_number
# return empty tuple for EOF
def get_next_token():
    Scanner.file.seek(max(0, Scanner.read_chars))
    Scanner.line += Scanner.buffered_new_lines
    Scanner.buffered_new_lines = 0

    dfa = DFA()
    lexeme = ""

    c = Scanner.file.read(1)
    print(c)
    # check_next_line(c)
    if c == '':
        return ()
    lexeme += c
    Scanner.read_chars += len(c.encode('utf-8'))
    suc = dfa.next_state(c)
    if not suc:
        return dfa.get_state_lexical_error(), lexeme, Scanner.line

    acc, stared = dfa.accept()
    if acc:
        # TOF
        if c == '*' and check_unmatched_comment():
            lexeme += '/'
            return LexicalError.UNMATCHED_COMMENT, lexeme, Scanner.line
        if stared:
            lexeme = lexeme[:-1]
            Scanner.read_chars -= len(c.encode('utf-8'))

        if lexeme == '\n' and dfa.get_accept_state_token_type(lexeme) == TokenType.WHITESPACE:
            Scanner.line += 1
            # Scanner.read_chars += 1

        token_type = dfa.get_accept_state_token_type(lexeme)
        if token_type == TokenType.ID or token_type == TokenType.KEYWORD:
            Scanner.symbols.add(lexeme)
        return token_type, lexeme, Scanner.line

    while c:
        c = Scanner.file.read(1)
        # check_next_line(c)
        lexeme += c
        Scanner.read_chars += len(c.encode('utf-8'))

        suc = dfa.next_state(c)
        if not suc:
            return dfa.get_state_lexical_error(), lexeme, Scanner.line

        acc, stared = dfa.accept()
        if acc:
            # TOF
            if c == '*' and check_unmatched_comment():
                lexeme += '/'
                return LexicalError.UNMATCHED_COMMENT, lexeme, Scanner.line

            if stared:
                lexeme = lexeme[:-1]
                Scanner.read_chars -= len(c.encode('utf-8'))

            if lexeme == "\n" and dfa.get_accept_state_token_type(lexeme) == TokenType.WHITESPACE:
                Scanner.line += 1
                # Scanner.read_chars += 1

            token_type = dfa.get_accept_state_token_type(lexeme)
            if token_type == TokenType.ID or token_type == TokenType.KEYWORD:
                Scanner.symbols.add(lexeme)
            return token_type, lexeme, Scanner.line
    acc, stared = dfa.accept()
    if acc:
        if stared:
            lexeme = lexeme[:-1]
            Scanner.read_chars -= 1
        return dfa.get_accept_state_token_type(lexeme), lexeme, Scanner.line

    return dfa.get_state_lexical_error(), lexeme, Scanner.line


def check_next_line(c):
    if c == '\n':
        Scanner.buffered_new_lines += 1


def check_unmatched_comment():
    lookahead = Scanner.file.read(1)
    Scanner.read_chars += 1
    if lookahead == '/':
        return True
    Scanner.read_chars -= 1
    return False


if __name__ == "__main__":
    last_token = (TokenType.COMMENT, "")
    while last_token:
        last_token = get_next_token()
