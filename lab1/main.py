from lexer import tokenize

file = open("test.java")

code = file.read()

arr = tokenize(code)

for target in arr:
    print(target)
