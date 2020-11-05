from lexer import tokenize, TokenType


def find_previous_significant_token_index(self, index):
    index -= 1
    while self.all_tokens[index].token_type == TokenType.WHITE_SPACE and index > 0:
        index -= 1
    if self.all_tokens[index].token_type == TokenType.WHITE_SPACE and index == 0:
        return -1
    return index


def find_next_significant_token_index(self, index):
    index += 1
    while index + 1 < len(self.all_tokens) and self.all_tokens[index].token_type == TokenType.WHITE_SPACE:
        index += 1
    if index >= len(self.all_tokens):
        return -1
    return index


keyword_type_value = ('int', 'short', 'bool', 'string', 'void')  # TODO


class File:
    def __init__(self, path):
        self.path = path
        file = open(path, encoding="utf-8")
        self.all_tokens = tokenize(file.read())


class StaticAnalyzer:

    def __init__(self, files):
        self.files = files

    # PascalCase
    def validate_pascal_case(self, token):
        print("validate_pascal_case ", token)
        index = 1
        while index < len(token.correct_token_value):
            if token.correct_token_value[index] == '_' and index + 1 < len(token.correct_token_value):
                if token.correct_token_value[index] == '_' and token.correct_token_value[index + 1] == '_':
                    token.correct_token_value = token.correct_token_value.replace('_', '', 1)
                    index -= 1
                else:
                    token.correct_token_value = token.correct_token_value[:index] + \
                                                token.correct_token_value[index + 1].upper() + \
                                                token.correct_token_value[index + 2:]
            index += 1
        token.correct_token_value = token.correct_token_value.replace('_', '')
        token.correct_token_value = token.correct_token_value.capitalize()
        print("validate_pascal_case ", token)

    def validate_interface(self, token):
        print("validate_interface ", token)


    def validate_camel_case(self, token):
        print("validate_camel_case", token)
        index = 1
        while index < len(token.correct_token_value):
            if token.correct_token_value[index] == '_' and index + 1 < len(token.correct_token_value):
                if token.correct_token_value[index] == '_' and token.correct_token_value[index + 1] == '_':
                    token.correct_token_value = token.correct_token_value.replace('_', '', 1)
                    index -= 1
                else:
                    token.correct_token_value = token.correct_token_value[:index] + \
                                                token.correct_token_value[index + 1].upper() + \
                                                token.correct_token_value[index + 2:]
            index += 1
        token.correct_token_value = token.correct_token_value.replace('_', '')
        token.correct_token_value = token.correct_token_value[0].lower() + token.correct_token_value[1:]
        print("validate_camel_case ", token)

    def validate_names(self, file):
        stack_influential_tokens = []
        was_const = False
        for index in range(len(file.all_tokens)):
            current_token = file.all_tokens[index]
            if current_token.token_value in ['class', 'enum', 'namespace', 'interface', '{', '[']:
                stack_influential_tokens.append(current_token)

            if current_token.token_value == 'const':
                was_const = True
            elif current_token.token_value in ['{', ';', '}', '=']:
                was_const = False

            if current_token.token_value == ']':
                stack_influential_tokens.pop()
            elif current_token.token_value == '}':
                stack_influential_tokens.pop()
                if len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value in \
                        ['class', 'enum', 'namespace', 'interface']:
                    stack_influential_tokens.pop()

            if current_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                previous_significant_token = file.all_tokens[find_previous_significant_token_index(file, index)]
                next_significant_token = file.all_tokens[find_next_significant_token_index(file, index)]
                if len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value in \
                        ['namespace', 'enum']:
                    self.validate_pascal_case(current_token)  # namespaces, classes, enums
                elif len(stack_influential_tokens) > 1 and previous_significant_token.token_value == 'class':
                    self.validate_pascal_case(current_token)  # classes
                elif len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value == 'interface':
                    self.validate_interface(current_token)  # interfaces
                elif len(stack_influential_tokens) > 1 and stack_influential_tokens[-1].token_value == '{' and \
                        stack_influential_tokens[-2] == 'enum':
                    self.validate_pascal_case(current_token)  # enum values
                # elif len(stack_influential_tokens) > 2 and stack_influential_tokens[-1].token_value == '[':
                #     if not (stack_influential_tokens[-2].token_value == '{' and
                #             stack_influential_tokens[-3].token_value == '{'):
                #         self.validate_pascal_case(current_token)
                elif len(stack_influential_tokens) > 1 and stack_influential_tokens[-1].token_value == '{' and \
                        stack_influential_tokens[-2].token_value in ['class', 'interface'] and \
                        (previous_significant_token.token_value in ['>', ']'] or
                         previous_significant_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS or
                         previous_significant_token.token_value in keyword_type_value):
                    if was_const:
                        self.validate_pascal_case(current_token)  # constants
                    elif next_significant_token.token_value in ['(', '{']:
                        self.validate_pascal_case(current_token)  # methods and properties
                    elif next_significant_token.token_value in [';', '=', ',', ')']:
                        self.validate_camel_case(current_token)  # object references
                elif len(stack_influential_tokens) > 4 and stack_influential_tokens[-2].token_value == '{' and \
                        stack_influential_tokens[-1].token_value == '{' and \
                        (previous_significant_token.token_value in ['>', ']'] or
                         previous_significant_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS or
                         previous_significant_token.token_value in keyword_type_value) and \
                        next_significant_token.token_value in [';', '=']:
                    self.validate_camel_case(current_token)  # object references in method

    def analyze(self):
        for file in self.files:
            self.validate_names(file)
