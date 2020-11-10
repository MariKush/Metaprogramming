import logging
import os
import sys
from os import listdir
from os.path import isfile, isdir, split, isabs
from pathlib import Path

from .lexer import TokenType, Token
from .static_analyzer import StaticAnalyzer, File, validate_pascal_case

__version__ = "0.3.0"


def get_files(path):
    return list(Path(path).rglob("*.cs"))


def get_files_not_rec(path):
    return list(Path(path).glob("*.cs"))


def write_result(all_tokens, file_name):
    new_file = open(file_name, "w", encoding='utf-8')
    for token in all_tokens:
        new_file.write(token.correct_token_value)
    new_file.close()


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
        write_result(file.all_tokens, file.path)


def fix_names(path):
    if isdir(path):
        os.chdir(path)
        for entry in listdir():
            fix_names(entry)
        os.chdir('..')
        name = split(path)[1]
        token = Token(None, name, None, None)
        validate_pascal_case(token)
        os.rename(name, token.correct_token_value)

    if isfile(path) and len(path) > 2 and path[-3:] == '.cs':
        if split(path)[1] != path:
            os.chdir(split(path)[0])
        name = split(path)[1]
        token = Token(None, name[:-3], None, None)
        validate_pascal_case(token)
        os.rename(name, token.correct_token_value + '.cs')


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
                print(file)
                my_files.append(File(file))

            analyze = StaticAnalyzer(my_files)
            analyze.analyze()

            if mode == 'v':
                verify(my_files)
            elif mode == 'f':
                fix(my_files)
                fix_names(sys.argv[3])
            else:
                print("Mode error")
