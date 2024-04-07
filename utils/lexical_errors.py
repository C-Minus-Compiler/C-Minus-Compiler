from enum import Enum

class LexicalError(Enum):
    INVALID_NUMBER = 'Invalid number'
    INVALID_INPUT = 'Invalid input'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'
