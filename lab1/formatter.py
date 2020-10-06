import json

from lexer import Token, TokenType


class Formatter:
    all_tokens = []

    around_operators = []

    template_data = None
    indent = None

    def load_template(self, template_file_name):
        template_file = open(template_file_name)
        self.template_data = json.load(template_file)

        tabs_and_indents = self.template_data['tabs_and_indents']
        self.indent = tabs_and_indents['indent']

        spaces_around_operators = self.template_data['spaces']['around_operators']

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

        if spaces_around_operators['multiplicative']:
            self.around_operators.extend(["*", "/", "%"])

        if spaces_around_operators['shift']:
            self.around_operators.extend(["<<", ">>", ">>>"])

        if spaces_around_operators['unary']:
            self.around_operators.extend(["!", "++", "--"])  # TODO add "+" and "-"

        if spaces_around_operators['lambda']:
            self.around_operators.extend(["->"])

        if spaces_around_operators['method_reference']:
            self.around_operators.extend(["::"])

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

    def add_spaces(self):
        self.add_spaces_before_parentheses()
        self.add_spaces_around_operators()

    def formatting(self):
        self.remove_all_spaces_and_tabs()
        # validate new lines
        # add tubs
        self.add_spaces()
