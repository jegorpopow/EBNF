from EBNF import *
import sys
import ebnf_parser


class Converter:
    names: Dict[str, Terminal]
    non_terminals: Set[str]
    rules: List[Rule]
    start: NonTerminal

    def __init__(self, grammar: EBNF):
        self.names = grammar.name_bindings
        self.non_terminals = grammar.non_terminals
        self.rules = grammar.rules
        self.start = grammar.start

    def compose_nt_name(self, expr: Expression) -> str:
        if isinstance(expr, Terminal) or isinstance(expr, NonTerminal) or isinstance(expr, Name):
            res = expr.value
        elif isinstance(expr, Eps):
            res = "eps"
        elif isinstance(expr, Optional):
            res = "opt" + self.compose_nt_name(expr.value)
        elif isinstance(expr, KleeneStar):
            res = "star" + self.compose_nt_name(expr.value)
        elif isinstance(expr, Alt):
            res = "(" + "|".join([self.compose_nt_name(e) for e in expr.vals]) + ")"
        elif isinstance(expr, Seq):
            res = "(" + ",".join(self.compose_nt_name(e) for e in expr.vals) + ")"
        else:
            raise RuntimeError("Can't match expression type during name composition")
        while res in self.non_terminals:
            res += "'"
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
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = input_file + ".out"

        with open(input_file, "r") as grammar_definition, open(output_file, "w") as processed_grammar:
            file = grammar_definition.readlines()
            ebnf_parser.parser.parse("".join(file))
            ebnf = make_grammar(ebnf_parser.Start, ebnf_parser.Rules, ebnf_parser.Bindings)
            cfg = Converter(ebnf).convert()
            print(show_grammar(cfg), file=processed_grammar)


if __name__ == "__main__":
    main()
