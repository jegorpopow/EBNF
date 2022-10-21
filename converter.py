import string

from EBNF import *
import ebnf_parser
import argparse
from random import choice


class Converter:
    names: Dict[str, Terminal]
    non_terminals: Set[str]
    rules: List[Rule]
    start: NonTerminal
    readable: bool
    composed_names: Dict[str, str] = {}

    def __init__(self, grammar: EBNF, readable: bool):
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
                res = "mult" + self.compose_nt_name(expr.value)
            elif isinstance(expr, Alt):
                res = "(" + "or".join([self.compose_nt_name(e) for e in expr.vals]) + ")"
            elif isinstance(expr, Seq):
                res = "(" + " ".join(self.compose_nt_name(e) for e in expr.vals) + ")"
            else:
                raise RuntimeError("Can't match expression type during name composition")
            while res in self.non_terminals:
                res += "'"
        else:
            str_expr = show(expr)
            res = self.composed_names.get(str_expr, '')
            if not res:
                res = choice(string.ascii_uppercase)
                while res in self.non_terminals:
                    res += choice(string.ascii_uppercase)
                self.non_terminals.add(res)
                self.composed_names[str_expr] = res
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
            if len(expr.vals) == 1:
                return self.convert_expr(expr.vals[0])
            converted_seq = [self.convert_expr(e) for e in expr.vals]
            converted, new_rules = reduce(lambda a, b: (make_seq(a[0], b[0]), a[1] + b[1]),
                                          converted_seq)
        else:
            raise RuntimeError("Can't match expression type during conversion")
        return converted, new_rules

    def remove_nested_seqs(self, expr: Expression) -> List[Expression]:
        if isinstance(expr, Seq):
            exprs = []
            for e in expr.vals:
                exprs += self.remove_nested_seqs(e)
            return exprs
        else:
            return [expr]

    def convert(self) -> EBNF:
        converted_rules_dict: Dict[str, Set[str]] = {}
        str_to_expr: Dict[str, Expression] = {}
        i = 0
        while i < len(self.rules):
            definition = self.rules[i].definition
            defined = self.rules[i].defined
            new_definition, new_rules = self.convert_expr(definition)
            str_new_definition = show(new_definition)
            str_defined = show(defined)
            str_to_expr[str_new_definition] = new_definition
            str_to_expr[str_defined] = defined
            converted_rules_dict[str_defined] = converted_rules_dict.get(str_defined, set()) | {
                str_new_definition}
            self.rules += new_rules
            i += 1
        for nt in converted_rules_dict:
            self.remove_chains(nt, {}, converted_rules_dict, str_to_expr)

        used_non_terminals_names = reduce(lambda lhs, rhs: lhs | rhs,
                                          [reduce(lambda lhs, rhs: lhs | rhs,
                                                  map(lambda s: collect_non_terminals(
                                                          str_to_expr[s]),
                                                      exprs)) for exprs in
                                           converted_rules_dict.values()])

        converted_rules = []
        for lhs, defs in converted_rules_dict.items():
            defined_nt = str_to_expr[lhs]
            if defined_nt.value in used_non_terminals_names or defined_nt.value == self.start.value:
                def_exprs = []
                for d in defs:
                    if isinstance(str_to_expr[d], Seq):
                        def_exprs.append(Seq(self.remove_nested_seqs(str_to_expr[d])))
                    else:
                        def_exprs.append(str_to_expr[d])
                if len(def_exprs) > 1:
                    d = Alt(def_exprs)
                else:
                    d = def_exprs[0]
                converted_rules.append(Rule(defined_nt, d))

        return make_grammar(self.start, converted_rules, [])

    def remove_chains(self, v: str, used: Dict[str, bool], graph: Dict[str, Set[str]],
                      to_expr: Dict[str, Expression]) -> Set[str]:
        if used.get(v, False):
            return graph.get(v, set())
        used[v] = True
        new_defs = set()
        for definition in graph[v]:
            expr = to_expr[definition]
            if isinstance(expr, NonTerminal):
                new_defs |= self.remove_chains(definition, used, graph, to_expr)
            else:
                new_defs.add(definition)
        graph[v] = new_defs
        return new_defs


def main():
    p = argparse.ArgumentParser("Converts CF formal grammar from EBNF to classic form")
    p.add_argument("-r", '--readable', dest='readable', action="store_true")
    p.add_argument('input', nargs=1, type=str)
    p.add_argument('output', nargs='?')
    args = p.parse_args()
    if not args.output:
        args.output = args.input[0] + ".out"
    ebnf = ebnf_parser.parse_ebnf(args.input[0])
    with open(args.output, "w") as processed_grammar:
        if ebnf is None:
            print("Grammar is incorrect, cannot parse",
                  file=processed_grammar)
        else:
            cfg = Converter(ebnf, args.readable).convert()
            print(show_grammar(cfg), file=processed_grammar)


if __name__ == "__main__":
    main()
