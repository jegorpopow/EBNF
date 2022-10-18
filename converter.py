from EBNF import *
import sys


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
        pass

    def convert_expr(self, expr: Expression) -> (Expression, List[Rule]):
        if isinstance(expr, Terminal) or isinstance(expr, NonTerminal) or isinstance(expr, Eps):
            converted = expr, new_rules = []
        elif isinstance(expr, Name):
            converted = self.names[expr.value], new_rules = []
        elif isinstance(expr, Optional):
            converted = NonTerminal(self.compose_nt_name(expr))
            new_rules = [Rule(converted, expr.value), Rule(converted, Seq([EPS]))]
        elif isinstance(expr, KleeneStar):
            converted = NonTerminal(self.compose_nt_name(expr))
            new_rules = [Rule(converted, Seq([converted, expr.value])), Rule(converted, Seq([EPS]))]
        elif isinstance(expr, Alt):
            converted = NonTerminal(self.compose_nt_name(expr))
            new_rules = [Rule(converted, e) for e in expr.vals]
        elif isinstance(expr, Seq):
            converted_seq = [self.convert_expr(e) for e in expr.vals]
            converted, new_rules = reduce(lambda e1, rs1, e2, rs2: (make_seq(e1, e2), rs1 + rs2),
                                          converted_seq)
        else:
            raise RuntimeError("ABOBUS")
        return converted, new_rules

    def convert(self) -> EBNF:
        converted_rules = []
        i = 0
        while i < len(self.rules):
            expr, rules = self.convert_expr(self.rules[i].definition)
            converted_rules.append(Rule(self.rules[i].defined, expr))
            self.rules += rules
            i += 1

        return make_grammar(self.start, converted_rules, [])


def main():
    pass


if __name__ == "__main__":
    main()
