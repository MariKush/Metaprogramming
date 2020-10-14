from enum import Enum

code = ""
size = None

start_pos_of_token = 0
end_pos_of_token = 0

current_row = 1
current_column = 0

all_tokens = []

keywords = ["abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const", "continue",
            "default", "do", "double", "else", "enum", "extends", "final", "finally", "float", "for",
            "if", "goto", "implements", "import", "instanceof", "int", "interface", "long",
            "native", "new", "package", "private", "protected", "public", "return",
            "short", "static", "strictfp", "super", "switch", "synchronized",
            "this", "throw", "throws", "transient", "try", "void", "volatile", "while"]

separators = ["(", ")", "{", "}", "[", "]", ";", ",", ".", "@"]

operators = [[">>>="],
             ["<<=", ">>=", ">>>", "..."],
             ["::", "->", "==", ">=", "<=", "!=", "&&", "||", "++", "--", "<<", ">>",
              "+=", "-=", "*=", "/=", "&=", "|=", "^=", "%="],
             ["=", ">", "<", "!", "~", "?", ":", "+", "-", "*", "/", "&", "|", "^", "%"]]


class TokenType(Enum):
    WHITE_SPACE = 0
    STRING = 1
    NUMBER_OR_IDENTIFIERS = 2
    KEYWORD = 3
    SEPARATOR = 4
    OPERATOR = 5
    COMMENT = 6


class Token:
    def __init__(self, token_type, token_value, row, column):
        self.token_type = token_type
        self.token_value = token_value
        self.row = row
        self.column = column

    def __repr__(self):
        return f'{self.token_type} {self.token_value} {self.row} {self.column}'


def add_space(c):
    global current_column, start_pos_of_token
    global current_row
    global all_tokens

    all_tokens.append(Token(TokenType.WHITE_SPACE, c, current_row, current_column))

    if c == '\n':
        current_row += 1
        current_column = 1
    elif c == ' ':
        current_column += 1
    elif c == '\t':
        current_column += 4 - (current_column - 1) % 4
    start_pos_of_token += 1


def add_token(token_type):
    global current_column
    global start_pos_of_token

    all_tokens.append(Token(token_type, code[start_pos_of_token: end_pos_of_token], current_row, current_column))
    current_column += end_pos_of_token - start_pos_of_token
    start_pos_of_token = end_pos_of_token


def add_string(quotes):
    global end_pos_of_token

    end_pos_of_token = start_pos_of_token + 1

    while code[end_pos_of_token] != quotes:
        if code[end_pos_of_token] == '\\':
            end_pos_of_token += 1
        end_pos_of_token += 1

    end_pos_of_token += 1
    add_token(TokenType.STRING)


def is_char_of_number_or_identifiers(char):
    return char.isdigit() or char.isalpha() or char == '.' or char == '_'


def add_number_or_identifiers():
    global end_pos_of_token

    end_pos_of_token = start_pos_of_token + 1

    while is_char_of_number_or_identifiers(code[end_pos_of_token]):
        end_pos_of_token += 1

    if code[start_pos_of_token: end_pos_of_token] in keywords:
        add_token(TokenType.KEYWORD)
    else:
        add_token(TokenType.NUMBER_OR_IDENTIFIERS)


def add_if_is_operator():
    global end_pos_of_token

    if code[start_pos_of_token: start_pos_of_token + 4] in operators[0]:
        end_pos_of_token = start_pos_of_token + 4
        add_token(TokenType.OPERATOR)
        return True
    elif code[start_pos_of_token: start_pos_of_token + 3] in operators[1]:
        end_pos_of_token = start_pos_of_token + 3
        add_token(TokenType.OPERATOR)
        return True
    elif code[start_pos_of_token: start_pos_of_token + 2] in operators[2]:
        end_pos_of_token = start_pos_of_token + 2
        add_token(TokenType.OPERATOR)
        return True
    elif code[start_pos_of_token: start_pos_of_token + 1] in operators[3]:
        end_pos_of_token = start_pos_of_token + 1
        add_token(TokenType.OPERATOR)
        return True
    return False


def can_add_comment():
    global end_pos_of_token, current_column, current_row
    end_pos_of_token = start_pos_of_token + 1

    if code[end_pos_of_token] == "/":
        while code[end_pos_of_token] != "\n":
            end_pos_of_token += 1
        add_token(TokenType.COMMENT)
        return True
    elif code[end_pos_of_token] == "*":
        end_pos_of_token += 1

        current_column_local = current_column
        current_row_local = current_row

        while code[end_pos_of_token] != "*" or code[end_pos_of_token + 1] != "/":
            current_column_local += 1
            if code[end_pos_of_token] == "\n":
                current_row_local += 1
                current_column_local = 1
            end_pos_of_token += 1

        end_pos_of_token += 2
        current_column_local += 2

        add_token(TokenType.COMMENT)
        current_column = current_column_local
        current_row = current_row_local
        return True
    return False


def tokenize(text):
    global code
    code = text
    global size
    size = len(code)

    global start_pos_of_token
    global end_pos_of_token
    global current_row
    global current_column

    while start_pos_of_token < size:
        c = code[start_pos_of_token]

        if c.isspace():
            add_space(c)

        elif c in ("'", '"'):
            add_string(c)

        elif c == "/" and can_add_comment():
            pass

        elif is_char_of_number_or_identifiers(c):
            add_number_or_identifiers()

        elif c in separators:
            end_pos_of_token = start_pos_of_token + 1
            add_token(TokenType.SEPARATOR)

        elif add_if_is_operator():
            pass

        else:
            print("Unexpected token: " + c)
            start_pos_of_token += 1

    return all_tokens
