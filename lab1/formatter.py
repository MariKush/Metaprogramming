import json


class Formatter:
    all_tokens = []

    indent = None

    def load_template(self, template_file_name):
        template_file = open(template_file_name)
        template_data = json.load(template_file)

        tabs_and_indents = template_data['tabs_and_indents']
        self.indent = tabs_and_indents['indent']

    def __init__(self, all_tokens, template_file_name="template.json"):
        self.load_template(template_file_name)
        self.all_tokens = all_tokens

    def remove_all_spaces_and_tabs(self):
        i = 0
        while i < len(self.all_tokens):
            if self.all_tokens[i].value in (' ', '\t'):
                self.all_tokens.pop(i)
            else:
                i += 1

    def formatting(self):
        self.remove_all_spaces_and_tabs()
        # validate new lines
        # add tubs
        # add spaces