# glob  : START start rest

# start : NON_TERMINAL BIND_END

# rest  : NAMES defs RULES rls
#       | RULES rls

# defs  : def
#       | defs def

# def   : NAME BIND TERMINAL BIND_END

# rls   : rule
#       | rls rule

# rule  : NON_TERMINAL BIND expr BIND_END

# expr  : seq
#       | expr ALT_SEP seq

# seq   : term
#       | seq term

# term  : NON_TERMINAL
#       | TERMINAL
#       | NAME
#       | LGROUP expr RGROUP
#       | LOPT expr ROPT
#       | LKLEENE expr RKLEENE
#       | EPSILON


from queue import Empty
import sys
from EBNF import *
from lexer import tokens
from ply import yacc as yacc
from sys import argv

global Start, Bindings, Rules

Start: NonTerminal
Bindings: List[NameBinding] = []
Rules: List[Rule] = []


def p_glob(p):
    """
    glob  : START start NAMES rest
    """
    p[0] = p[4]


def p_rest(p):
    """
    rest  : defs RULES rls
          | RULES rls
    """
    global Bindings, Rules

    if len(p) == 3:
        Rules = p[2]
        p[0] = p[2]
    else:
        Bindings = p[1]
        Rules = p[3]
        p[0] = p[1]


def p_start(p):
    """
    start : NON_TERMINAL BIND_END
    """
    global Start

    Start = NonTerminal(p[1])


def p_defs(p):
    """
    defs  : def
          | defs def
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]


def p_def(p):
    """
    def   : NAME BIND TERMINAL BIND_END
    """
    p[0] = NameBinding(Name(p[1]), Terminal(p[3]))


def p_rls(p):
    """
    rls   : rule
          | rls rule
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]


def p_rule(p):
    """
    rule  : NON_TERMINAL BIND expr BIND_END
    """
    p[0] = Rule(NonTerminal(p[1]), p[3])


def p_expr(p):
    """
    expr  : seq
          | expr ALT_SEP seq
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = make_alt(p[3], p[1])


def p_seq(p):
    """
    seq   : term
          | seq term
    """
    if len(p) == 2:
        p[0] = Seq([p[1]])
    else:
        p[0] = make_seq(p[1], p[2])


def p_term_nt(p):
    """
    term : NON_TERMINAL
    """
    p[0] = NonTerminal(p[1])


def p_term_t(p):
    """
    term : TERMINAL
    """
    p[0] = Terminal(p[1])


def p_term_n(p):
    """
    term : NAME
    """
    p[0] = Name(p[1])


def p_term_e(p):
    """
    term : EPSILON
    """
    p[0] = Eps()


def p_term_g(p):
    """
    term : LGROUP expr RGROUP
    """
    p[0] = p[2]


def p_term_k(p):
    """
    term : LKLEENE expr RKLEENE
    """
    p[0] = KleeneStar(p[2])


def p_term_o(p):
    """
    term : LOPT expr ROPT
    """
    p[0] = Optional(p[2])


global parser
global output_file_opened


def p_error(p):
    if p == None:
        token = "end of file"
        parser.errok()
    else:
        token = f"{p.type}({p.value}) on line {p.lineno}"

    print(f"Syntax error: Unexpected {token}", file=output_file_opened)


def parse_ebnf(input_file: str, debug_output: str = "parser_debug.out") -> Union[EBNF, None]:
    global parser
    parser = yacc.yacc(debugfile=debug_output)

    with open(input_file, "r") as grammar_definition:
        file = grammar_definition.readlines()
        parser.parse("".join(file))
        try:
            ebnf = make_grammar(Start, Rules, Bindings)
            return ebnf
        except TypeError or ValueError:
            return None


def main():
    global parser, output_file_opened

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = input_file + ".out"

        output_file_opened = open(output_file, "w")
        ebnf = parse_ebnf(input_file, output_file)

        if ebnf is None:
            print("Grammar is incorrect, cannot parse",
                  file=output_file_opened)
        else:
            print(show_grammar(ebnf), file=output_file_opened)

        output_file_opened.close()
    else:
        print("Expected at least one argument: input file containing grammar")


if __name__ == "__main__":
    main()
