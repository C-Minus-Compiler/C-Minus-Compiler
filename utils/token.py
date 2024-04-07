from enum import Enum


class TokenType(Enum):
    NUM = "NUM"
    ID = "ID"
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"


class TokenRegex(Enum):
    digit = r'^\d$',
    alphabet = r'^[a-zA-Z]$',
    keyword = r'^if|else|void|int|repeat|break|until|return$',
    symbol = r'^;|:|\[|]|\(|\)|{|}|\+|-|\*|=|<|,$',
    whitespace = r'^\n|\r|\t|\v|\f| $',
    new_line = r'^\n$',
    slash = r'^/$',
    star = r'^\*$',
    single_line_comment_starter = r'^//$',
    multi_line_comment_starter = r'^/\*$',
    multi_line_comment_finisher = r'^\*/$',
    equal_sign = r'^=$'
