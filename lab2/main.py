import sys
from pathlib import Path

from lexer import tokenize, TokenType, Token
from static_analyzer import StaticAnalyzer, File


def get_files(path):
    return list(Path(path).rglob("*.cs"))


def get_files_not_rec(path):
    return list(Path(path).glob("*.cs"))


def write_result(all_tokens, file_name):
    new_file = open(file_name, "w")
    for i in all_tokens:
        new_file.write(i.token_value)


analyze = StaticAnalyzer([File('Test.cs')])
analyze.analyze()
#
# for filename in get_files("C:\\Users\\Dell-admin\\Desktop\\Fleck-master\\src\\Fleck"):
#     file = open(filename)
#     print(filename)
#     all_tokens = tokenize(file.read())
#
#     # print(all_tokens)
