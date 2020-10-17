import sys
from pathlib import Path

from formatter import Formatter
from lexer import tokenize, TokenType, Token


def get_files(path):
    return list(Path(path).rglob("*.java"))


def write_result(all_tokens, file_name):
    new_file = open(file_name, "w")
    for i in all_tokens:
        new_file.write(i.token_value)


def friendship_with_tabs_and_spaces(use_tab_character, indent, initial_sequence_of_tokens):
    if use_tab_character:
        current_token_index = 0
        number_of_consecutive_spaces = 0
        while current_token_index < len(initial_sequence_of_tokens):
            if initial_sequence_of_tokens[current_token_index].token_value == " ":
                number_of_consecutive_spaces += 1
            else:
                number_of_consecutive_spaces = 0

            if number_of_consecutive_spaces == indent:
                current_token_index -= indent
                for i in range(indent):
                    initial_sequence_of_tokens.pop(current_token_index)
                initial_sequence_of_tokens.insert(current_token_index, Token(TokenType.WHITE_SPACE, "\t", None, None))
                current_token_index += 1

            current_token_index += 1
    else:
        current_token_index = 0
        while current_token_index < len(initial_sequence_of_tokens):
            if initial_sequence_of_tokens[current_token_index].token_value == "\t":
                initial_sequence_of_tokens.pop(current_token_index)
                for i in range(indent):
                    initial_sequence_of_tokens.insert(current_token_index,
                                                      Token(TokenType.WHITE_SPACE, " ", None, None))
                current_token_index -= 1
                current_token_index += indent
            current_token_index += 1


error_id = 0


def verify_sequence_of_tokens(file_name, initial_sequence_of_tokens, formatted_sequence_of_tokens):
    global error_id
    errors = open("errors.log", "w+")
    index_in_initial_sequence = 0
    index_in_formatted_sequence = 0
    while index_in_initial_sequence < len(initial_sequence_of_tokens):
        current_initial_token = initial_sequence_of_tokens[index_in_initial_sequence]
        current_formatted_token = formatted_sequence_of_tokens[index_in_formatted_sequence]
        if current_initial_token.token_value == current_formatted_token.token_value:
            index_in_initial_sequence += 1
            index_in_formatted_sequence += 1
        else:
            error_message = "Error Message"
            if current_initial_token.token_type == TokenType.WHITE_SPACE and \
                    current_formatted_token.token_type != TokenType.WHITE_SPACE:
                error_message = "too match white space"
                index_in_initial_sequence += 1
            elif current_initial_token.token_type != TokenType.WHITE_SPACE and \
                    current_formatted_token.token_type == TokenType.WHITE_SPACE:
                error_message = "not enough white space"
                index_in_formatted_sequence += 1
            elif current_initial_token.token_type == TokenType.WHITE_SPACE and \
                    current_formatted_token.token_type == TokenType.WHITE_SPACE and \
                    current_initial_token.token_value != current_formatted_token.token_value:
                if current_initial_token.token_value == "\n":
                    index_in_formatted_sequence += 1
                    error_message = "not enough spaces"
                elif current_formatted_token.token_value == "\n":
                    index_in_initial_sequence += 1
                    error_message = "extra space characters"
                else:
                    error_message = "mismatch of white space values"
            errors.write(f"{error_id}.{file_name} Path: Line Number: {current_initial_token.row} "
                         f"Error Code: {error_message}.\n")
            error_id += 1


def console_interface():
    if len(sys.argv) == 1:
        print("Warning! You have entered too few arguments.")
    else:
        if sys.argv[1] in ["-h", "--help"]:
            print("""
------------------------HELP------------------------

python main.py --verify template name -(p|d|f) /..
python main.py -v template name  -(p|d|f) /..
python main.py --format template name -(p|d|f) /..
python main.py -f template name -(p|d|f) /.. 
python main.py --help
python main.py -h

-p - project
-d - directory
-f - file
/.. - path to project, directory or file"""
                  )
        else:
            if sys.argv[1] in ["-v", "--verify"]:
                mode = 'v'
            else:
                mode = 'f'
            template_name = sys.argv[2]

            if sys.argv[3] == '-f':
                files = [sys.argv[4]]
            else:
                files = get_files(sys.argv[4])

            for filename in files:
                try:
                    print(filename)
                    file = open(filename, encoding='utf-8', errors='ignore')
                    code = file.read()
                    all_tokens = tokenize(code)
                    formatter = Formatter(all_tokens.copy(), template_name)
                    all_tokens_after_formatting = formatter.formatting()

                    if mode == 'f':
                        write_result(all_tokens_after_formatting, filename)
                    else:
                        friendship_with_tabs_and_spaces(
                            formatter.template_data['tabs_and_indents']['use_tab_character'],
                            formatter.indent, all_tokens)
                        verify_sequence_of_tokens(filename, all_tokens, all_tokens_after_formatting)
                except:
                    print(f"unexpected error in {filename} file")
