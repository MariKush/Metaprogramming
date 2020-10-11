import json

from lexer import Token, TokenType


class Formatter:
    all_tokens = []

    around_operators = []

    template_data = None
    indent = None
    spaces_around_unary_operator = None
    spaces_around_additive_operator = None
    spaces_around_relational_operator = None

    def add_template_for_around_operators(self, spaces_around_operators):
        if spaces_around_operators['assignment']:
            self.around_operators.extend(["=", "+=", "-=", "*=", "/=", "&=", "|=", "^=", "%=", ">>>=", "<<=", ">>="])

        if spaces_around_operators['logical']:
            self.around_operators.extend(["&&", "||"])

        if spaces_around_operators['equality']:
            self.around_operators.extend(["==", "!="])

        if spaces_around_operators['relational']:
            self.around_operators.extend(["<=", ">="])
        self.spaces_around_relational_operator = spaces_around_operators['relational']

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

    def find_next_significant_token_index(self, index):
        index += 1
        while self.all_tokens[index].token_type == TokenType.WHITE_SPACE and index + 1 < len(self.all_tokens):
            index += 1
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

        # for template
        number_open_brackets = 0
        current_token_index = 0
        while current_token_index < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value == '<':
                token_value = self.all_tokens[self.find_next_significant_token_index(current_token_index)].token_value
                if token_value[0].isalpha() and token_value[0].isupper():
                    number_open_brackets += 1
                    pass
                else:
                    if self.spaces_around_relational_operator:
                        self.add_white_space(current_token_index)
                        self.add_white_space(current_token_index + 2)
                        current_token_index += 2
            elif self.all_tokens[current_token_index].token_value == '>':
                if number_open_brackets > 0:
                    number_open_brackets -= 1
                    if number_open_brackets == 0:
                        current_token_index += 1
                        if self.all_tokens[current_token_index].token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                            current_token_index += 1
                            if self.all_tokens[current_token_index].token_value != '(':
                                self.add_white_space(current_token_index - 1)
                                current_token_index += 1
                else:
                    if self.spaces_around_relational_operator:
                        self.add_white_space(current_token_index)
                        self.add_white_space(current_token_index + 2)
                        current_token_index += 2
            current_token_index += 1

    def add_spaces_before_class_and_method_left_brace(self):
        spaces_before_class_left_brace = self.template_data['spaces']['before_left_brace']['class']
        spaces_before_method_left_brace = self.template_data['spaces']['before_left_brace']['method']
        current_token_index = 0
        while current_token_index < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value == 'class':
                while self.all_tokens[current_token_index].token_value != '{':
                    current_token_index += 1
                if spaces_before_class_left_brace:
                    self.add_white_space(current_token_index)
                    current_token_index += 1

            if self.all_tokens[current_token_index].token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                if self.all_tokens[current_token_index + 1].token_value == '(' and \
                        (self.all_tokens[current_token_index - 1].token_type in [TokenType.KEYWORD,
                                                                                 TokenType.NUMBER_OR_IDENTIFIERS] \
                         or self.all_tokens[current_token_index - 1].token_value in ['>', ']']):
                    if spaces_before_method_left_brace:
                        while self.all_tokens[current_token_index].token_value != '{':
                            current_token_index += 1
                        self.add_white_space(current_token_index)
                        current_token_index += 1

            current_token_index += 1

    def add_spaces_before_left_brace(self):
        all_from_spaces_before_left_brace = []
        selected_keywords = []
        json_before_left_brace = self.template_data['spaces']['before_left_brace']
        for key in json_before_left_brace:
            all_from_spaces_before_left_brace.append(key)

        for key in all_from_spaces_before_left_brace[2:]:
            if json_before_left_brace[key]:
                selected_keywords.append(key)

        current_token_index = 0
        while current_token_index + 1 < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value in selected_keywords:
                number_of_open_parentheses = 0
                current_token_index += 1
                while self.all_tokens[current_token_index].token_value == ' ':
                    current_token_index += 1

                if self.all_tokens[current_token_index].token_value == "(":
                    number_of_open_parentheses += 1
                    current_token_index += 1
                while number_of_open_parentheses > 0:
                    if self.all_tokens[current_token_index].token_value == "(":
                        number_of_open_parentheses += 1
                    elif self.all_tokens[current_token_index].token_value == ")":
                        number_of_open_parentheses -= 1
                    current_token_index += 1

                while self.all_tokens[current_token_index].token_value == ' ':
                    current_token_index += 1
                if self.all_tokens[current_token_index].token_value == '{':
                    self.add_white_space(current_token_index)
            current_token_index += 1

        self.add_spaces_before_class_and_method_left_brace()

    def add_spaces_before_keywords(self):
        selected_keywords = []
        json_before_keywords = self.template_data['spaces']['before_keyword']
        for key in json_before_keywords:
            if json_before_keywords[key]:
                selected_keywords.append(key)

        current_token_index = 0
        while current_token_index + 1 < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value in selected_keywords and \
                    self.all_tokens[current_token_index - 1].token_value == "}":
                self.add_white_space(current_token_index)
                current_token_index += 1
            current_token_index += 1

    def add_spaces_in_ternary_operator(self):
        json_in_ternary_operator = self.template_data['spaces']['in_ternary_operator']
        current_token_index = 0

        def get_column_index(local_current_token_index):
            local_current_token_index += 1
            i = 0
            while i < 20 and local_current_token_index + 1 < len(self.all_tokens):
                i += 1
                if self.all_tokens[local_current_token_index].token_value == ':':
                    return local_current_token_index
                local_current_token_index += 1
            return -1

        while current_token_index + 1 < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value == '?':
                colon_index = get_column_index(current_token_index)
                if colon_index > -1:
                    if json_in_ternary_operator['after_colon']:
                        self.add_white_space(colon_index + 1)
                    if json_in_ternary_operator['before_colon']:
                        self.add_white_space(colon_index)
                    if json_in_ternary_operator['after_question_mark']:
                        self.add_white_space(current_token_index + 1)
                    if json_in_ternary_operator['before_question_mark']:
                        self.add_white_space(current_token_index)
                    current_token_index += 1
            current_token_index += 1

    def add_spaces_other(self):
        json_other = self.template_data['spaces']['other']
        current_token_index = 0
        while current_token_index + 1 < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value == ',':
                if json_other['after_comma']:
                    self.add_white_space(current_token_index + 1)
                if json_other['before_comma']:
                    self.add_white_space(current_token_index)
            current_token_index += 1

        current_token_index = 0
        while current_token_index + 1 < len(self.all_tokens):
            if self.all_tokens[current_token_index].token_value in ['for', 'try']:
                number_of_open_parentheses = 0
                current_token_index += 1
                while self.all_tokens[current_token_index].token_value == ' ':
                    current_token_index += 1
                if self.all_tokens[current_token_index].token_value == "(":
                    number_of_open_parentheses += 1
                    current_token_index += 1
                    while number_of_open_parentheses > 0:
                        if self.all_tokens[current_token_index].token_value == "(":
                            number_of_open_parentheses += 1
                        if self.all_tokens[current_token_index].token_value == ")":
                            number_of_open_parentheses -= 1
                        if self.all_tokens[current_token_index].token_value == ";":
                            if json_other['after_for_semicolon']:
                                self.add_white_space(current_token_index + 1)
                            if json_other['before_for_semicolon']:
                                self.add_white_space(current_token_index)
                                current_token_index += 1
                        if self.all_tokens[current_token_index].token_value == ":":
                            if json_other['after_colon_in_foreach']:
                                self.add_white_space(current_token_index + 1)
                            if json_other['before_colon_in_foreach']:
                                self.add_white_space(current_token_index)
                                current_token_index += 1
                        current_token_index += 1
            current_token_index += 1

        if json_other['after_type_cast']:
            current_token_index = 0
            while current_token_index + 1 < len(self.all_tokens):
                if self.all_tokens[current_token_index].token_value == '(':
                    current_token_index += 1
                    if self.all_tokens[current_token_index].token_type in [TokenType.NUMBER_OR_IDENTIFIERS,
                                                                           TokenType.KEYWORD]:
                        current_token_index += 1
                        if self.all_tokens[current_token_index].token_value == '[':
                            current_token_index += 2
                        if self.all_tokens[current_token_index].token_value == ')' and \
                                self.all_tokens[current_token_index + 1].token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                            self.add_white_space(current_token_index + 1)
                            current_token_index += 1
                current_token_index += 1

    def add_spaces(self):
        self.add_spaces_before_parentheses()
        self.add_spaces_around_operators()
        self.add_spaces_before_left_brace()
        self.add_spaces_before_keywords()
        self.add_spaces_in_ternary_operator()
        self.add_spaces_other()

    def formatting(self):
        self.remove_all_spaces_and_tabs()
        # validate new lines
        # add tubs
        self.add_spaces()




