import sys
from ply.lex import TOKEN
import ply.lex as lex
from tokens import *
import logging

logging.basicConfig(
    filename="lex.log", level=logging.WARNING, filemode="w"
)

reserved = {"start:": "START", "rules:": "RULES", "names:": "NAMES", "EPS": "EPSILON"}

tokens = (
    [
        "TERMINAL",
        "NON_TERMINAL",
        "NAME",
        "BIND",
        "ALT_SEP",
        "BIND_END",
        "BIND_BEGIN",
    ]
    + ["L" + name for name in ["KLEENE", "OPT", "GROUP"]]
    + ["R" + name for name in ["KLEENE", "OPT", "GROUP"]]
    + list(reserved.values())
)

t_LKLEENE = LKLEENE_REGEX
t_RKLEENE = RKLEENE_REGEX

t_LOPT = LOPT_REGEX
t_ROPT = ROPT_REGEX

t_LGROUP = LGROUP_REGEX
t_RGROUP = RGROUP_REGEX

t_BIND = BIND_REGEX
t_BIND_END = BIND_END_REGEX
t_ALT_SEP = ALT_SEP_REGEX
t_BIND_BEGIN = r"[ ][ ]"

t_ignore = ""


def t_newline(token):
    r"\n+"
    token.lexer.lineno += len(token.value)


def t_error(token):
    logging.warning(
        f"Illegal character {token.value[0]} at position {token.lexer.lexpos} at line {token.lexer.lineno}"
    )
    token.lexer.skip(1)


@TOKEN(TERMINAL_REGEX)
def t_TERMINAL(token):
    token.value = token.value[1:-1]
    return token


@TOKEN(NON_TERMINAL_REGEX)
def t_NON_TERMINAL(token):
    token.value = token.value[1:-1]
    return token


@TOKEN(NAME_REGEX)
def t_NAME(token):
    token.value = token.value[1:]
    return token


@TOKEN(KEYWORD_REGEX)
def t_KEYWORD(token):
    token.type = reserved.get(token.value)
    if token.type is None:
        token = t_error(token)
    return token


lexer = lex.lex()


def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = input_file + ".out"

        with open(input_file, "r") as grammar_definition, open(
            output_file, "w"
        ) as processed_grammar:
            lexer.input("".join(grammar_definition.readlines()))

            while True:
                tok = lexer.token()
                if not tok:
                    break
                print(tok, file=processed_grammar)

    else:
        print(
            "Incorrect usage. Please, specify input file in first argument, e.g: 'lex.py input_file.txt'"
        )


if __name__ == "__main__":
    main()
