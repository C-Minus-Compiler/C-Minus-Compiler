import re

from utils.token import TokenType


class Scanner:
    INPUT = "input.txt"
    code = open(INPUT, 'r')
    line = 0
    char = 0
    read_chars = 0 # refers to chars read by far


class DFA:
    start = 0
    current_state = 0
    states = (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    accept_states = (2, 4, 5, 7, 8, 11, 14, 15) 
    stared_states = (2, 4, 8)

    # (state, "regex", "true means should be false means should not be", "next_state")
    transitions = ((0, r'[0-9]', True, 1),
                   (1, r'[0-9]', False, 2),
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
        for trn in self.transitions:
            if self.current_state == trn[0] and (trn[2] if re.match(trn[1], c) != None else not trn[2]):
                self.current_state = trn[2]
                return True
        return False
    
    # returns: Bool, Bool (accept, stared)
    def accept(self):
        return self.current_state in self.accept_states, self.current_state in self.stared_states


# returns: TokenType, lexeme, line_number
# return empty tuple for EOF
def get_next_token():
    return TokenType.ID, "dutchman", 0
