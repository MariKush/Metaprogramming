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

    def add_new_line(self, position):
        self.all_tokens.insert(position, Token(TokenType.WHITE_SPACE, "\n", None, None))

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

    def add_new_line_if_necessary(self, current_token_index):
        if self.all_tokens[current_token_index + 1].token_value != "\n":
            self.add_new_line(current_token_index + 1)

    def add_indent(self, current_token_index, indent):
        for i in range(indent):
            self.add_white_space(current_token_index)

    def validate_new_lines_and_tabs(self):
        current_token_index = 0
        stack_influential_tokens = []
        indent = 0
        current_indent = 0  # if, for, while, do without "{}"
        switch_indent = 0
        was_new_line = False
        while current_token_index + 1 < len(self.all_tokens):
            current_token_value = self.all_tokens[current_token_index].token_value

            if was_new_line and not ("switch" in stack_influential_tokens and
                                     current_token_value in ["case", "default"]):
                was_new_line = False
                if current_token_value == "}":
                    indent -= self.indent
                self.add_indent(current_token_index, indent + current_indent + switch_indent)
                current_token_index += indent + current_indent + switch_indent
                current_indent = 0
                if current_token_value == "}":
                    indent += self.indent

            if current_token_value == ";":
                if not (len(stack_influential_tokens) != 0 and stack_influential_tokens[-1] == "("):
                    self.add_new_line_if_necessary(current_token_index)

            elif current_token_value in ["for", "try", "if", "else", "while", "do", "switch"]:
                stack_influential_tokens.append(current_token_value)

            elif current_token_value == "{":
                indent += self.indent
                switch_indent = 0
                current_indent = 0
                stack_influential_tokens.append(current_token_value)
                if self.all_tokens[current_token_index - 1].token_value not in ["]", "(", "="]:
                    # for array and annotation
                    self.add_new_line_if_necessary(current_token_index)

            elif current_token_value == "}":
                while stack_influential_tokens.pop() != "{":
                    pass
                indent -= self.indent
                if self.all_tokens[current_token_index + 1].token_value not in \
                        ["else", "while", "finally", "catch", ")", ";"]:
                    self.add_new_line_if_necessary(current_token_index)

            if was_new_line and "switch" in stack_influential_tokens and current_token_value in ["case", "default"]:
                switch_indent = 0
                self.add_indent(current_token_index, indent + current_indent + switch_indent)
                current_token_index += indent + current_indent + switch_indent
                was_new_line = False

            elif current_token_value == ":" and \
                    (self.all_tokens[current_token_index - 2].token_value == "case" or
                     self.all_tokens[current_token_index - 1].token_value == "default"):
                if self.all_tokens[current_token_index + 1].token_value != '{':
                    switch_indent = self.indent
                    self.add_new_line(current_token_index + 1)

            elif current_token_value == "(":
                stack_influential_tokens.append(current_token_value)

            elif current_token_value == ")":
                while stack_influential_tokens.pop() != "(":
                    pass

            elif current_token_value == "\n":
                was_new_line = True

            elif current_token_value == "@":
                current_token_index += 2

                if self.all_tokens[current_token_index].token_value == "(":
                    current_token_index += 1
                    number_of_open_parentheses = 1
                    while number_of_open_parentheses > 0:
                        if self.all_tokens[current_token_index].token_value == "(":
                            number_of_open_parentheses += 1
                        elif self.all_tokens[current_token_index].token_value == ")":
                            number_of_open_parentheses -= 1
                        current_token_index += 1

                if not (len(stack_influential_tokens) != 0 and stack_influential_tokens[-1] == "("):
                    current_token_index -= 1
                    self.add_new_line_if_necessary(current_token_index)
                # current_token_index -= 1

            current_token_index += 1

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
                                                                                 TokenType.NUMBER_OR_IDENTIFIERS]
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

                if self.all_tokens[current_token_index].token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                    current_token_index += 1

                while number_of_open_parentheses > 0:
                    if self.all_tokens[current_token_index].token_value == "(":
                        number_of_open_parentheses += 1
                    elif self.all_tokens[current_token_index].token_value == ")":
                        number_of_open_parentheses -= 1
                    current_token_index += 1

                while self.all_tokens[current_token_index].token_value == ' ':
                    current_token_index += 1

                if self.all_tokens[current_token_index].token_value == ":":
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

    def add_spaces_within(self):
        all_from_within = []
        selected_keywords = []
        json_within = self.template_data['spaces']['within']
        for key in json_within:
            all_from_within.append(key)

        for key in all_from_within[:7]:
            if json_within[key]:
                selected_keywords.append(key)

        # if, for, while, switch, try, catch, synchronized
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

                self.add_white_space(current_token_index)
                current_token_index += 1

                while number_of_open_parentheses > 0:
                    if self.all_tokens[current_token_index].token_value == "(":
                        number_of_open_parentheses += 1
                    elif self.all_tokens[current_token_index].token_value == ")":
                        number_of_open_parentheses -= 1
                    current_token_index += 1

                self.add_white_space(current_token_index - 1)
                current_token_index += 1

            current_token_index += 1

        if self.template_data['spaces']['within']['annotation_parentheses']:
            current_token_index = 0
            while current_token_index + 1 < len(self.all_tokens):
                if self.all_tokens[current_token_index].token_value == "@":
                    current_token_index += 2
                    while self.all_tokens[current_token_index].token_value == ' ':
                        current_token_index += 1
                    if self.all_tokens[current_token_index].token_value == "(":
                        number_of_open_parentheses = 1
                        current_token_index += 1
                        self.add_white_space(current_token_index)
                        current_token_index += 1
                        while number_of_open_parentheses > 0:
                            if self.all_tokens[current_token_index].token_value == "(":
                                number_of_open_parentheses += 1
                            elif self.all_tokens[current_token_index].token_value == ")":
                                number_of_open_parentheses -= 1
                            current_token_index += 1
                        self.add_white_space(current_token_index - 1)
                        current_token_index += 1

                current_token_index += 1

        if self.template_data['spaces']['within']['angle_brackets']:
            current_token_index = 0
            while current_token_index + 1 < len(self.all_tokens):
                next_token_value = \
                    self.all_tokens[self.find_next_significant_token_index(current_token_index)].token_value[0]
                if self.all_tokens[current_token_index].token_value == "<" and \
                        next_token_value.isalpha() and next_token_value.isupper():
                    number_of_open_parentheses = 1
                    current_token_index += 1
                    self.add_white_space(current_token_index)
                    current_token_index += 1
                    while number_of_open_parentheses > 0:
                        if self.all_tokens[current_token_index].token_value == "<":
                            number_of_open_parentheses += 1
                        elif self.all_tokens[current_token_index].token_value == ">":
                            number_of_open_parentheses -= 1
                        current_token_index += 1
                    self.add_white_space(current_token_index - 1)
                    current_token_index += 1

                current_token_index += 1

        if self.template_data['spaces']['within']['empty_method_call_parentheses']:
            current_token_index = 1
            while current_token_index + 1 < len(self.all_tokens):
                if self.all_tokens[current_token_index].token_value == "(" and \
                        self.all_tokens[current_token_index - 1].token_type == TokenType.NUMBER_OR_IDENTIFIERS and \
                        self.all_tokens[current_token_index + 1].token_value == ")" and \
                        self.all_tokens[self.find_next_significant_token_index(current_token_index + 1)].token_value \
                        not in ["{", "->"]:
                    current_token_index += 1
                    self.add_white_space(current_token_index)
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

        if json_other['after_type_cast'] or self.template_data['spaces']['within']['type_cast_parentheses']:
            current_token_index = 0
            while current_token_index + 1 < len(self.all_tokens):
                if self.all_tokens[current_token_index].token_value == '(':
                    current_token_index += 1
                    open_parentheses = current_token_index
                    if self.all_tokens[current_token_index].token_type in [TokenType.NUMBER_OR_IDENTIFIERS,
                                                                           TokenType.KEYWORD]:
                        current_token_index += 1
                        if self.all_tokens[current_token_index].token_value == '[':
                            current_token_index += 2
                        if self.all_tokens[current_token_index].token_value == ')' and \
                                self.all_tokens[current_token_index + 1].token_type == TokenType.NUMBER_OR_IDENTIFIERS:
                            if self.template_data['spaces']['within']['type_cast_parentheses']:
                                self.add_white_space(current_token_index)
                                self.add_white_space(open_parentheses)
                                current_token_index += 2
                            if json_other['after_type_cast']:
                                self.add_white_space(current_token_index + 1)
                                current_token_index += 1
                current_token_index += 1

    def add_spaces_between_tokens(self):
        current_token_index = 0
        while current_token_index + 1 < len(self.all_tokens):
            if (self.all_tokens[current_token_index].token_type in
                    [TokenType.NUMBER_OR_IDENTIFIERS, TokenType.KEYWORD] or
                self.all_tokens[current_token_index].token_value == "]") and \
                    (self.all_tokens[current_token_index + 1].token_type in
                     [TokenType.NUMBER_OR_IDENTIFIERS, TokenType.KEYWORD] or
                     self.all_tokens[current_token_index + 1].token_value == "@"):
                self.add_white_space(current_token_index + 1)
                current_token_index += 1
            current_token_index += 1

    def add_spaces(self):
        self.add_spaces_before_parentheses()
        self.add_spaces_around_operators()
        self.add_spaces_before_left_brace()
        self.add_spaces_before_keywords()
        self.add_spaces_within()
        self.add_spaces_in_ternary_operator()
        self.add_spaces_other()
        self.add_spaces_between_tokens()

    def formatting(self):
        self.remove_all_spaces_and_tabs()
        self.validate_new_lines_and_tabs()
        self.add_spaces()
        return self.all_tokens
