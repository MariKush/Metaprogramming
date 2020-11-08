from .lexer import tokenize, TokenType, Token


def find_previous_significant_token_index(file, index):
    index -= 1
    while file.all_tokens[index].token_type == TokenType.WHITE_SPACE and index > 0:
        index -= 1
    if file.all_tokens[index].token_type == TokenType.WHITE_SPACE and index == 0:
        return -1
    return index


def find_next_significant_token_index(file, index):
    index += 1
    while index + 1 < len(file.all_tokens) and file.all_tokens[index].token_type == TokenType.WHITE_SPACE:
        index += 1
    if index >= len(file.all_tokens):
        return -1
    return index


keyword_type_value = ('int', 'short', 'bool', 'string', 'void', 'char', 'ulong', 'byte', 'decimal', 'double',
                      'sbyte', 'float', 'long', 'uint', 'ushort')


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
        token.correct_token_value = token.correct_token_value[0].upper() + token.correct_token_value[1:]

    def validate_interface(self, token):
        self.validate_pascal_case(token)
        if token.correct_token_value[0] != 'I':
            token.correct_token_value = 'I' + token.correct_token_value
        else:
            token.correct_token_value = token.correct_token_value[0] + \
                                        token.correct_token_value[1].upper() + \
                                        token.correct_token_value[2:]

    def validate_camel_case(self, token):
        self.validate_pascal_case(token)
        token.correct_token_value = token.correct_token_value[0].lower() + token.correct_token_value[1:]

    def rename_all(self, token_for_rename):
        for file in self.files:
            for token in file.all_tokens:
                if token.token_value == token_for_rename.token_value:
                    token.correct_token_value = token_for_rename.correct_token_value

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
                    self.validate_pascal_case(current_token)  # namespaces, enums
                    self.rename_all(current_token)
                elif len(stack_influential_tokens) > 1 and previous_significant_token.token_value == 'class':
                    self.validate_pascal_case(current_token)  # classes
                    self.rename_all(current_token)
                elif len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value == 'interface':
                    self.validate_interface(current_token)  # interfaces
                    self.rename_all(current_token)
                elif len(stack_influential_tokens) > 1 and stack_influential_tokens[-1].token_value == '{' and \
                        stack_influential_tokens[-2] == 'enum':
                    self.validate_pascal_case(current_token)  # enum values
                    self.rename_all(current_token)
                elif len(stack_influential_tokens) > 1 and stack_influential_tokens[-1].token_value == '{' and \
                        stack_influential_tokens[-2].token_value in ['class', 'interface'] and \
                        (previous_significant_token.token_value in ['>', ']'] or
                         previous_significant_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS or
                         previous_significant_token.token_value in keyword_type_value):
                    if was_const:
                        self.validate_pascal_case(current_token)  # constants
                        self.rename_all(current_token)
                    elif next_significant_token.token_value in ['(', '{']:
                        self.validate_pascal_case(current_token)  # methods and properties
                        self.rename_all(current_token)
                    elif next_significant_token.token_value in [';', '=', ',', ')']:
                        self.validate_camel_case(current_token)  # object references
                        self.rename_all(current_token)
                elif len(stack_influential_tokens) > 4 and stack_influential_tokens[-2].token_value == '{' and \
                        stack_influential_tokens[-1].token_value == '{' and \
                        (previous_significant_token.token_value in ['>', ']'] or
                         previous_significant_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS or
                         previous_significant_token.token_value in keyword_type_value) and \
                        next_significant_token.token_value in [';', '=']:
                    self.validate_camel_case(current_token)  # object references in method
                    self.rename_all(current_token)

    def validate_doc_text(self, text):
        result = ''
        try:
            stack = []
            index = 0
            while index < len(text):
                if text[index] == '<':
                    start_pos_of_token = index
                    index += 1
                    if text[index] == '/':
                        while index < len(text):
                            if text[index] == '>':
                                if text[start_pos_of_token + 2:index] == stack[-1][0][1:stack[-1][0].find(' ')]:
                                    if len(stack) > 1:
                                        stack[-2][1] += stack[-1][0] + stack[-1][1] + \
                                                        text[start_pos_of_token:index + 1]
                                    else:
                                        if len(result) > 0:
                                            result += '\n'
                                        result += stack[-1][0] + stack[-1][1] + text[start_pos_of_token:index + 1]
                                stack.pop()
                                break
                            index += 1
                    else:
                        index = text.find('>', index)
                        stack.append([text[start_pos_of_token:index + 1], ''])
                elif len(stack) > 0:
                    stack[-1][1] += text[index]

                index += 1

            return result
        except Exception as e:
            return result

    def get_valid_documentation(self, file, index):
        indent = 0
        row = 0
        document_comments = []
        while file.all_tokens[index].correct_token_value not in ['{', '}', ';']:
            if file.all_tokens[index].correct_token_value[:3] == '///':
                indent = file.all_tokens[index].column - 1
                row = file.all_tokens[index].row
                document_comments.insert(0, file.all_tokens[index].correct_token_value)
                file.all_tokens.pop(index)
                index -= 1
                while file.all_tokens[index].correct_token_value in [' ', '\t']:
                    file.all_tokens.pop(index)
                    index -= 1
                if file.all_tokens[index].correct_token_value == '\n':
                    file.all_tokens.pop(index)
                    index -= 1
                index += 1

            index -= 1

        if indent == 0:
            indent = file.all_tokens[find_next_significant_token_index(file, index)].column - 1
        document_comments_text = ''
        for line in document_comments:
            if len(document_comments_text) > 0:
                document_comments_text += '\n'
            document_comments_text += line[3:]

        correct_documentation = self.validate_doc_text(document_comments_text)
        return correct_documentation, indent, row, index, document_comments

    def add_documented_comment(self, file, index, correct_documentation, indent, row, comments_before):
        ind = 0
        document_comments = correct_documentation.split('\n')
        for doc_line in document_comments:
            index += 1
            for i in range(indent):
                file.all_tokens.insert(index, Token(TokenType.WHITE_SPACE, ' ', None, None))
                index += 1

            curr_index = 0
            while curr_index < len(doc_line) and doc_line[curr_index].isspace():
                curr_index += 1
            comment_str = '/// ' + doc_line[curr_index:]
            file.all_tokens.insert(index, Token(TokenType.COMMENT, "", row, indent + 1))
            if ind < len(comments_before):
                file.all_tokens[index].token_value = comments_before[ind]
            file.all_tokens[index].correct_token_value = comment_str
            index += 1
            file.all_tokens.insert(index, Token(TokenType.WHITE_SPACE, '\n', None, None))
            row += 1
            ind += 1

    # class, interface, enum
    def validate_doc_type_comment(self, name_index, word_type, file):
        name = file.all_tokens[name_index].correct_token_value
        index = name_index
        correct_documentation, indent, row, index, document_comments = self.get_valid_documentation(file, index)

        if correct_documentation.find('<summary>') == -1:
            correct_documentation = '<summary>\n' + name + \
                                    f' {word_type} description here\n</summary>' + correct_documentation

        index = find_next_significant_token_index(file, index)
        while file.all_tokens[index].token_value != '\n':
            index -= 1

        self.add_documented_comment(file, index, correct_documentation, indent, row, document_comments)

        while True:
            if file.all_tokens[index].correct_token_value == name:
                return index
            index += 1

    def validate_doc_method_comment(self, name_index, file):
        name = file.all_tokens[name_index].correct_token_value
        index = name_index

        param_index = name_index
        params = []
        while file.all_tokens[param_index].token_value != '(':
            param_index += 1
        while file.all_tokens[param_index].token_value != ')':
            if file.all_tokens[param_index + 1].token_value in [',', ')']:
                params.append(file.all_tokens[param_index].correct_token_value)
            param_index += 1

        correct_documentation, indent, row, index, documents_comments = self.get_valid_documentation(file, index)

        if correct_documentation.find('<summary>') == -1:
            correct_documentation = '<summary>\n' + name + \
                                    ' method description here\n</summary>\n' + correct_documentation

        corr_index = 0
        pattern = '<param name="'
        while corr_index + len(pattern) < len(correct_documentation):
            if correct_documentation[corr_index:corr_index+len(pattern)] == pattern:
                corr_index = corr_index+len(pattern)
                start_of_name = corr_index
                while correct_documentation[corr_index] != '"':
                    corr_index += 1
                name = correct_documentation[start_of_name:corr_index]
                if name in params:
                    params.pop(params.index(name))
            corr_index += 1

        for param in params:
            correct_documentation = correct_documentation + '\n' + pattern + param + \
                                    '"> parameter description here </param>'

        index = find_next_significant_token_index(file, index)
        while file.all_tokens[index].token_value != '\n':
            index -= 1

        self.add_documented_comment(file, index, correct_documentation, indent, row, documents_comments)

    def validate_documentation(self, file):
        stack_influential_tokens = []
        index = 0
        while index < len(file.all_tokens):
            current_token = file.all_tokens[index]
            if current_token.token_value in ['class', 'enum', 'namespace', 'interface', '{', '[']:
                stack_influential_tokens.append(current_token)
            elif current_token.token_value == ']':
                stack_influential_tokens.pop()
            elif current_token.token_value == '}':
                stack_influential_tokens.pop()
                if len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value in \
                        ['class', 'enum', 'namespace', 'interface']:
                    stack_influential_tokens.pop()

            if current_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                previous_significant_token = file.all_tokens[find_previous_significant_token_index(file, index)]
                next_significant_token = file.all_tokens[find_next_significant_token_index(file, index)]
                if len(stack_influential_tokens) > 0 and stack_influential_tokens[-1].token_value in ['enum',
                                                                                                      'class',
                                                                                                      'interface']:
                    self.validate_doc_type_comment(index, stack_influential_tokens[-1].token_value, file)
                elif len(stack_influential_tokens) > 1 and stack_influential_tokens[-1].token_value == '{' and \
                        stack_influential_tokens[-2].token_value in ['class', 'interface', 'enum'] and \
                        (previous_significant_token.token_value in ['>', ']'] or
                         previous_significant_token.token_type == TokenType.NUMBER_OR_IDENTIFIERS or
                         previous_significant_token.token_value in keyword_type_value):
                    if next_significant_token.token_value == '(':
                        self.validate_doc_method_comment(index, file)  # methods
                    if next_significant_token.token_value == '{':
                        self.validate_doc_type_comment(index, 'property', file)  # properties
                    elif next_significant_token.token_value in [';', '=']:
                        self.validate_doc_type_comment(index, 'object reference', file)  # object references
            index += 1

    def analyze(self):
        for file in self.files:
            self.validate_names(file)
            self.validate_documentation(file)
