#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, List, Set, Union, Any, Dict
from functools import reduce


# This file contains some classes which present EBNF syntax features


# Expressions elements

TExpression = TypeVar("TExpression", bound="Expression")

@dataclass
class Eps:
  pass
EPS : Eps = Eps()

@dataclass
class Terminal:
    value : str

@dataclass
class NonTerminal:
    value : str

@dataclass
class Name:
    value : str

@dataclass
class Optional:
    value : TExpression

@dataclass
class KleeneStar:
    value : TExpression

SeqElement = Union[Eps, NonTerminal, Terminal, Name, Optional, KleeneStar] 

@dataclass
class Seq:
    vals : List[TExpression]

@dataclass
class Alt:
    vals : List[TExpression]


Expression = Union[Eps, NonTerminal, Terminal, Name, Optional, KleeneStar, Seq, Alt]


def show(expr: Expression) -> str:
    if isinstance(expr, Eps):
        return "EPS"
    elif isinstance(expr, Terminal):
        return f"\"{expr.value}\""
    elif isinstance(expr, Name):
        return f"${expr.value}"
    elif isinstance(expr, NonTerminal):
        return f"<{expr.value}>"
    elif isinstance(expr, Optional):
        return f"[{show(expr.value)}]"
    elif isinstance(expr, KleeneStar):
        return "{" + show(expr.value) + "}"
    elif isinstance(expr, Seq):
        return "(" + " ".join(map(show, expr.vals)) + ")"
    elif isinstance(expr, Alt):
        return "(" + " | ".join(map(show, expr.vals)) + ")"
    else:
        raise ValueError("Expression is not valid")


def make_seq(lhs : Expression, rhs : Expression) -> Seq:
    if isinstance(lhs, Seq):
        return Seq(lhs.vals + [rhs])
    return Seq([lhs, rhs])

def make_alt(lhs : Expression, rhs : Expression) -> Alt:
    if isinstance(lhs, Alt):
        return Alt(lhs.vals + [rhs])
    return Alt([lhs, rhs])

def collect_non_terminals(expr : Expression) -> Set[str]:
    if isinstance(expr, Eps) or isinstance(expr, Terminal) or isinstance(expr, Name):
        return set()
    elif isinstance(expr, NonTerminal):
        return {expr.value}
    elif isinstance(expr, Optional) or isinstance(expr, KleeneStar):
        return collect_non_terminals(expr.value)
    elif isinstance(expr, Seq) or isinstance(expr, Alt):
        return reduce(lambda lhs, rhs: lhs | rhs, map(collect_non_terminals, expr.vals))
    else:
        raise ValueError("Expression is not valid")

def collect_terminals(expr : Expression) -> Set[str]:
    if isinstance(expr, Eps) or isinstance(expr, NonTerminal) or isinstance(expr, Name):
        return set()
    elif isinstance(expr, Terminal):
        return {expr.value}
    elif isinstance(expr, Optional) or isinstance(expr, KleeneStar):
        return collect_non_terminals(expr.value)
    elif isinstance(expr, Seq) or isinstance(expr, Alt):
        return reduce(lambda lhs, rhs: lhs | rhs, map(collect_non_terminals, expr.vals))
    else:
        raise ValueError("Expression is not valid")
    
# Rule class

@dataclass
class Rule:
    defined : NonTerminal
    definition : Expression

# Name binding class

@dataclass
class NameBinding:
    defined : Name
    definition : Terminal


def collect_macros(bindings : List[NameBinding]) -> Dict[str, Terminal]:
    return {binding.defined.value : binding.definition for binding in bindings}
    

# EBNF class

@dataclass
class EBNF:
    start : NonTerminal
    terminals : Set[str]
    non_terminals : Set[str]
    rules : List[Rule]
    name_bindings : Dict[str, Terminal]

def make_grammar(start: NonTerminal, rules : List[Rule], bindings : List[NameBinding]) -> EBNF:
    name_bindings = collect_macros(bindings)

    terminals = (reduce(lambda lhs, rhs: lhs | rhs,
                       map(lambda rule: collect_terminals(rule.definition),
                           rules))
                | set(map(lambda terminal: terminal.value, name_bindings.values())))

    non_terminals = (reduce(lambda lhs, rhs: lhs | rhs,
                            map(lambda rule: collect_non_terminals(rule.definition),
                                rules))
                    | set(map(lambda rule: rule.defined.value, rules)))
    return EBNF(start, terminals, non_terminals, rules, name_bindings)


def show_grammar(grammar : EBNF) -> str:
    nl = "\n"
    bindings = "".join([f" ${name} := {show(grammar.name_bindings[name])};{nl}" for name in grammar.name_bindings])
   # bindings = "".join(map(lambda binding: f"  ${binding} := {show(grammar.name_bindings[binding]}{nl}" , grammar.name_bindings))
    rules = "".join(map(lambda rule: f"  {show(rule.defined)} := {show(rule.definition)};{nl}" , grammar.rules))
    return f"start:{nl}  {show(grammar.start)};{nl}names:{nl}{bindings}rules:{nl}{rules}"

def main():
   rule1 = Rule(NonTerminal("ABOBA"), Alt([Seq([KleeneStar(Terminal("a")), Optional(Name("bbb"))]), NonTerminal("c")]))
   rule2 = rule2 = Rule(NonTerminal("S"), Alt([Seq([Terminal("("), NonTerminal("S"), Terminal(")"), NonTerminal("S")]), EPS]))
   grammar = make_grammar(NonTerminal("S"), [rule1, rule2], [])
   print(show_grammar(grammar))


if __name__ == "__main__":
    main()

  





