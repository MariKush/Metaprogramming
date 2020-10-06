from formatter import Formatter
from lexer import tokenize

file = open("test.java")

code = file.read()

arr = tokenize(code)

formatter = Formatter(arr)
formatter.formatting()


def write_result(all_tokens):
    new_file = open("test_result.java", "w")
    for i in all_tokens:
        new_file.write(i.token_value)


write_result(formatter.all_tokens)

# for target in arr:
# print(target)
