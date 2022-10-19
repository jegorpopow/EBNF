import string

from EBNF import *
import sys
import ebnf_parser
import argparse
from random import choice


class Converter:
    names: Dict[str, Terminal]
    non_terminals: Set[str]
    rules: List[Rule]
    start: NonTerminal
    readable : bool

    def __init__(self, grammar: EBNF, readable : bool):
        self.names = grammar.name_bindings
        self.non_terminals = grammar.non_terminals
        self.rules = grammar.rules
        self.start = grammar.start
        self.readable = readable

    def compose_nt_name(self, expr: Expression) -> str:
        if not self.readable:
            if isinstance(expr, Terminal) or isinstance(expr, NonTerminal) or isinstance(expr, Name):
                res = expr.value
            elif isinstance(expr, Eps):
                res = "eps"
            elif isinstance(expr, Optional):
                res = "opt" + self.compose_nt_name(expr.value)
            elif isinstance(expr, KleeneStar):
                res = "star" + self.compose_nt_name(expr.value)
            elif isinstance(expr, Alt):
                res = "(" + " or ".join([self.compose_nt_name(e) for e in expr.vals]) + ")"
            elif isinstance(expr, Seq):
                res = "(" + ",".join(self.compose_nt_name(e) for e in expr.vals) + ")"
            else:
                raise RuntimeError("Can't match expression type during name composition")
            while res in self.non_terminals:
                res += "'"
        else:
            res = choice(string.ascii_uppercase)
            while res in self.non_terminals:
                res += choice(string.ascii_uppercase)
            self.non_terminals.add(res)
        return res

    def convert_expr(self, expr: Expression) -> (Expression, List[Rule]):
        if isinstance(expr, Terminal) or isinstance(expr, NonTerminal) or isinstance(expr, Eps):
            converted = expr
            new_rules = []
        elif isinstance(expr, Name):
            converted = self.names[expr.value]
            new_rules = []
        elif isinstance(expr, Optional):
            converted = NonTerminal(self.compose_nt_name(expr))
            new_rules = [Rule(converted, expr.value), Rule(converted, EPS)]
        elif isinstance(expr, KleeneStar):
            converted = NonTerminal(self.compose_nt_name(expr))
            new_rules = [Rule(converted, Seq([converted, expr.value])), Rule(converted, EPS)]
        elif isinstance(expr, Alt):
            converted = NonTerminal(self.compose_nt_name(expr))
            new_rules = [Rule(converted, e) for e in expr.vals]
        elif isinstance(expr, Seq):
            converted_seq = [self.convert_expr(e) for e in expr.vals]
            converted, new_rules = reduce(lambda a, b: (make_seq(a[0], b[0]), a[1] + b[1]),
                                          converted_seq)
        else:
            raise RuntimeError("Can't match expression type during conversion")
        return converted, new_rules

    def convert(self) -> EBNF:
        converted_rules = []
        i = 0
        while i < len(self.rules):
            rule_expr = self.rules[i].definition
            if not isinstance(rule_expr, Seq) and not isinstance(rule_expr, Alt):
                rule_expr = Seq([rule_expr])
            expr, rules = self.convert_expr(rule_expr)
            converted_rules.append(Rule(self.rules[i].defined, expr))
            self.rules += rules
            i += 1

        return make_grammar(self.start, converted_rules, [])


def main():
    p = argparse.ArgumentParser("Converts CF formal grammar from EBNF to classic form")
    p.add_argument("-r", '--readable', dest='readable', action="store_true")
    p.add_argument('input', nargs=1, type=str)
    p.add_argument('output', nargs='?')
    args = p.parse_args()
    if not args.output:
        args.output = args.input[0] + ".out"
    with open(args.input[0], "r") as grammar_definition, open(args.output, "w") as processed_grammar:
        file = grammar_definition.readlines()
        ebnf_parser.parser.parse("".join(file))
        ebnf = make_grammar(ebnf_parser.Start, ebnf_parser.Rules, ebnf_parser.Bindings)
        cfg = Converter(ebnf, args.readable).convert()
        print(show_grammar(cfg), file=processed_grammar)


if __name__ == "__main__":
    main()
