import scanner
from utils.token import TokenType


class CodeReader:
    def __init__(self, code_file_path):
        self.code = open(code_file_path, "r")
        self.input_code = self.code.read()


# def pre_initialized():
#     INPUT = "input.txt"
#     TOKENS = "tokens.txt"
#     LEXICAL_ERRORS = "lexical_errors.txt"
#     SYMBOL_TABLE = "symbol_table.txt"
#
#     code = open(INPUT, "r")
#
#     tokens = open(TOKENS, "w")
#
#     lexical_errors = open(LEXICAL_ERRORS, "w")
#     symbol_table = open(SYMBOL_TABLE, "w")
#
#     last_token = (TokenType.COMMENT, "", 0)
#     line_buffer = []
#     last_line = 0
#
#     dummy_counter = 0
#
#     while last_token:
#         last_token = scanner.get_next_token()
#         if last_line != last_token[2]:
#             print_line_tokens(tokens, line_buffer)
#             last_line = last_token[1]
#             line_buffer = []
#
#         if (last_token[0] != TokenType.WHITESPACE and last_token[0] != TokenType.COMMENT):
#             line_buffer.append(last_token)
#
#         # TODO: Remove the following
#         dummy_counter += 1
#         if dummy_counter > 10:
#             break
#
#     print_line_tokens(tokens, line_buffer)
#
#     symbol_table.close()
#     lexical_errors.close()
#     tokens.close()
#     code.close()


def main():
    INPUT = "input.txt"

    code_reader = CodeReader(INPUT)
    scanner.run(code_reader.input_code)


if __name__ == "__main__":
    main()
