import json

from lexer import Token, TokenType


class Formatter:
    all_tokens = []

    around_operators = []

    template_data = None
    indent = None
    spaces_around_unary_operator = None
    spaces_around_additive_operator = None

    def add_template_for_around_operators(self, spaces_around_operators):
        if spaces_around_operators['assignment']:
            self.around_operators.extend(["=", "+=", "-=", "*=", "/=", "&=", "|=", "^=", "%=", ">>>=", "<<=", ">>="])

        if spaces_around_operators['logical']:
            self.around_operators.extend(["&&", "||"])

        if spaces_around_operators['equality']:
            self.around_operators.extend(["==", "!="])

        if spaces_around_operators['relational']:
            self.around_operators.extend(["<=", ">="])  # TODO ">" and "<"

        if spaces_around_operators['bitwise']:
            self.around_operators.extend(["&", "|", "^"])

        self.spaces_around_additive_operator = spaces_around_operators['additive']

        if spaces_around_operators['multiplicative']:
            self.around_operators.extend(["*", "/", "%"])

        if spaces_around_operators['shift']:
            self.around_operators.extend(["<<", ">>", ">>>"])

        if spaces_around_operators['unary']:
            self.around_operators.extend(["!", "++", "--"])
        self.spaces_around_unary_operator = spaces_around_operators['unary']

        if spaces_around_operators['lambda']:
            self.around_operators.extend(["->"])

        if spaces_around_operators['method_reference']:
            self.around_operators.extend(["::"])

    def load_template(self, template_file_name):
        template_file = open(template_file_name)
        self.template_data = json.load(template_file)

        tabs_and_indents = self.template_data['tabs_and_indents']
        self.indent = tabs_and_indents['indent']

        spaces_around_operators = self.template_data['spaces']['around_operators']
        self.add_template_for_around_operators(spaces_around_operators)



    def __init__(self, all_tokens, template_file_name="template.json"):
        self.load_template(template_file_name)
        self.all_tokens = all_tokens

    def add_white_space(self, position):
        self.all_tokens.insert(position, Token(TokenType.WHITE_SPACE, " ", None, None))

    def remove_all_spaces_and_tabs(self):
        i = 0
        while i < len(self.all_tokens):
            if self.all_tokens[i].token_value in (' ', '\t'):
                self.all_tokens.pop(i)
            else:
                i += 1

    def find_previous_significant_token_index(self, index):
        index -= 1
        while self.all_tokens[index].token_type == TokenType.WHITE_SPACE and index > 0:
            index -= 1
        return index


    def add_spaces_before_parentheses(self):
        selected_keywords = []
        json_before_parentheses = self.template_data['spaces']['before_parentheses']
        for key in json_before_parentheses:
            if json_before_parentheses[key]:
                selected_keywords.append(key)

        current_token_index = 0
        while current_token_index + 1 < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value in selected_keywords and \
                    self.all_tokens[current_token_index + 1].token_value == '(':
                self.add_white_space(current_token_index + 1)
                current_token_index += 1
            current_token_index += 1


    def add_spaces_around_operators(self):
        current_token_index = 0
        while current_token_index < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value in self.around_operators:
                self.add_white_space(current_token_index)
                self.add_white_space(current_token_index + 2)
                current_token_index += 2
            current_token_index += 1

        current_token_index = 0
        while current_token_index < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value in ('-', '+'):
                previous_significant_token_value = \
                    self.all_tokens[self.find_previous_significant_token_index(current_token_index)]
                if previous_significant_token_value.token_type != TokenType.OPERATOR or \
                        previous_significant_token_value.token_value in ('++', '--'):  # in means additive operator
                    if self.spaces_around_additive_operator:
                        self.add_white_space(current_token_index)
                        self.add_white_space(current_token_index + 2)
                        current_token_index += 2
                else:
                    if self.spaces_around_unary_operator:
                        self.add_white_space(current_token_index)
                        self.add_white_space(current_token_index + 2)
                        current_token_index += 2
            current_token_index += 1

    def add_spaces(self):
        self.add_spaces_before_parentheses()
        self.add_spaces_around_operators()

    def formatting(self):
        self.remove_all_spaces_and_tabs()
        # validate new lines
        # add tubs
        self.add_spaces()
