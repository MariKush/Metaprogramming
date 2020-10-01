code = None
size = None

start_pos_of_token = 0
end_pos_of_token = None

current_row = 1
current_column = 0

all_tokens = []


class TokenType:
    white_space = 0
    operator = 1


class Token:
    def __init__(self, token_type, token_value, row, column):
        self.token_type = token_type
        self.token_value = token_value
        self.row = row
        self.column = column


def add_space(c):
    global current_column
    global current_row
    global all_tokens

    all_tokens.append(Token(TokenType.white_space, c, current_row, current_column))

    if c == '\n':
        current_row += 1
        current_column = 1
    elif c == ' ':
        current_column += 1
    elif c == '\t':
        current_column += 4 - (current_column - 1) % 4


def tokenize(text):
    global code
    code = text
    global size
    size = len(code)

    global start_pos_of_token
    global end_pos_of_token
    global current_row

    while start_pos_of_token < size:
        c = code[start_pos_of_token]

        if c.isspace():
            add_space(c)
