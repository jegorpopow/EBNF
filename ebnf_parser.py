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
    start : BIND_BEGIN NON_TERMINAL BIND_END
    """
    global Start
    Start = NonTerminal(p[2])


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
    def   : BIND_BEGIN NAME BIND TERMINAL BIND_END
    """
    p[0] = NameBinding(Name(p[2]), Terminal(p[4]))


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
    rule  : BIND_BEGIN NON_TERMINAL BIND expr BIND_END
    """
    p[0] = Rule(NonTerminal(p[2]), p[4])


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


parser = yacc.yacc()


def p_error(p):
    if p == None:
        token = "end of file"
        parser.errok()
    else:
        token = f"{p.type}({p.value}) on line {p.lineno}"

    print(f"Syntax error: Unexpected {token}")


def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = input_file + ".out"

        with open(input_file, "r") as grammar_definition, open(output_file, "w") as processed_grammar:
            file = grammar_definition.readlines()
            parser.parse("".join(file))
            ebnf = make_grammar(Start, Rules, Bindings)
            print(show_grammar(ebnf), file=processed_grammar)


if __name__ == "__main__":
    main()
