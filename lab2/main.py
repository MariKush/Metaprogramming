import logging
import os
import sys
from pathlib import Path

from lexer import TokenType
from static_analyzer import StaticAnalyzer, File


def get_files(path):
    return list(Path(path).rglob("*.cs"))


def get_files_not_rec(path):
    return list(Path(path).glob("*.cs"))


def write_result(all_tokens, file_name):
    new_file = open(file_name, "w")
    for token in all_tokens:
        new_file.write(token.correct_token_value)


def verify(files):
    for file in files:
        head, tail = os.path.split(file.path)
        logging.basicConfig(filename="verification.log")
        error_id = 0
        for token in file.all_tokens:
            if token.token_type != TokenType.WHITE_SPACE and \
                    token.token_value != token.correct_token_value:
                if token.token_type == TokenType.COMMENT:
                    error_type = "Documentation error"
                else:
                    error_type = "Name error"
                error_id += 1
                logging.warning(str(error_id) + " " + tail + " " + str(token.row) + " " + error_type + " " + str(token))


def fix(files):
    for file in files:
        head, tail = os.path.split(file.path)
        logging.basicConfig(filename="fixing.log")
        error_id = 0
        for token in file.all_tokens:
            if token.token_type != TokenType.WHITE_SPACE and \
                    token.token_value != token.correct_token_value:
                if token.token_type == TokenType.COMMENT:
                    error_type = "Change documentation"
                else:
                    error_type = "Fix name"
                error_id += 1
                logging.warning(str(error_id) + " " + tail + " " + str(token.row) + " " + error_type + " " + str(token))


def main():
    if len(sys.argv) == 1:
        print("Warning! You have entered too few arguments.")
    else:
        if sys.argv[1] in ["-h", "--help"]:
            print("""
    ------------------------HELP------------------------
    CSharpССF --verify -(p|d|f) /..
    CSharpССF -v  -(p|d|f) /..
    CSharpССF --fix -(p|d|f) /..
    CSharpССF -f -(p|d|f) /.. 
    CSharpССF --help
    CSharpССF -h
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

            if sys.argv[2] == '-f':
                files = [sys.argv[3]]
            elif sys.argv[2] == '-d':
                files = get_files_not_rec(sys.argv[3])
            else:
                files = get_files(sys.argv[3])

            my_files = []

            for file in files:
                my_files.append(File(file))

            analyze = StaticAnalyzer(my_files)
            analyze.analyze()

            if mode == 'v':
                verify(my_files)
            elif mode == 'f':
                fix(my_files)
            else:
                print("Mode error")

main()