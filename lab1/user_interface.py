import sys
from pathlib import Path

from formatter import Formatter
from lexer import tokenize


def get_files(path):
    return list(Path(path).rglob("*.java"))


def write_result(all_tokens, file_name):
    new_file = open(file_name, "w")
    for i in all_tokens:
        new_file.write(i.token_value)


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
                file = open(filename)
                code = file.read()
                all_tokens = tokenize(code)
                formatter = Formatter(all_tokens.copy(), template_name)
                all_tokens_after_formatting = formatter.formatting()

                if mode == 'f':
                    write_result(all_tokens_after_formatting, filename)

