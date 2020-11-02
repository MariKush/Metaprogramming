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


keyword_type_value = ('int', 'short', 'bool', 'string')  # TODO


class File:
    def __init__(self, path):
        self.path = path
        file = open(path, encoding="utf-8")
        self.all_tokens = tokenize(file.read())


class StaticAnalyzer:

    def __init__(self, files):
        self.files = files

    def validate_camel_case_first_up(self, token):
        pass

    def validate_interface(self, token):
        pass

    def validate_names(self, file):
        stack_influential_tokens = []
        for index in range(len(file.all_tokens)):
            current_token = file.all_tokens[index]
            if current_token.token_value in ['class', 'enum', 'namespace', 'interface', '{']:
                stack_influential_tokens.append(current_token)

            if current_token.token_value == '}':
                stack_influential_tokens.pop()
                if len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value in \
                        ['class', 'enum', 'namespace', 'interface']:
                    stack_influential_tokens.pop()

            if current_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                previous_significant_token = file.all_tokens[find_previous_significant_token_index(file, index)]
                if len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value in \
                        ['namespace', 'class', 'enum']:
                    self.validate_camel_case_first_up(current_token)
                elif len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value == 'interface':
                    self.validate_interface(current_token)
                elif len(stack_influential_tokens) > 1 and stack_influential_tokens[-1].token_value == '{' and \
                        stack_influential_tokens[-2] in ['class', 'interface'] and \
                        (previous_significant_token.token_value in ['>', ']'] or
                            previous_significant_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS or
                            previous_significant_token.token_value in keyword_type_value):
                    pass
                # TODO for field method property

    def analyze(self):
        for file in self.files:
            self.validate_names(file)
