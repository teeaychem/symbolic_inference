import unittest

from tree_sitter import Language, Parser
import tree_sitter_math

from typing import Optional

import cvc5
from cvc5 import Kind

class EquivalenceChecker:
    """
    Checks two formulas given as strings for equality by parsing the formulas to cvc5 terms and proving equivalence.
    In principle, at least, as by default a resource limit of 10 minutes is imposed.

    Divsion and integer division are supported, and both require a non-zero denominator for a counterexample.

    Messages are printed to on a failed parse, and a counterexample is printed on proof of inequality.
    """

    def __init__(self):
        self.variable_map = {}  # A map from variable strings to variable terms
        self.solver = cvc5.Solver()
        self.solver.setOption('tlimit-per', '600000')  # The time limit per call to check, in miliseconds
        self.solver.setOption('produce-models', 'true')
        self.parser = Parser(Language(tree_sitter_math.language()))

    def add_variable(self, v):
        variable = self.solver.mkConst(self.solver.getRealSort(), v)
        self.variable_map[v] = variable

        return variable

    def add_variables(self, vec):
        for v in vec:
            self.add_variable(v)


    def get_variable(self, variable_string):
        if variable_string in self.variable_map:
            return self.variable_map[variable_string]
        else:
            return self.add_variable(variable_string)

    def parse_expression(self, expression):
        """
        Recursively transform an expression to a cvc5 term.
        """
        if expression.type != "expression":
            return False

        expressed = expression.named_children[0]

        match expressed.type:
            case "add":
                parsed_l = self.parse_expression(expressed.named_child(0))
                parsed_r = self.parse_expression(expressed.named_child(1))
                if not (parsed_l and parsed_r):
                    return False

                return self.solver.mkTerm(Kind.ADD, parsed_l, parsed_r)

            case "sub":
                parsed_l = self.parse_expression(expressed.named_child(0))
                parsed_r = self.parse_expression(expressed.named_child(1))
                if not (parsed_l and parsed_r):
                    return False

                return self.solver.mkTerm(Kind.SUB, parsed_l, parsed_r)

            case "mul":
                parsed_l = self.parse_expression(expressed.named_child(0))
                parsed_r = self.parse_expression(expressed.named_child(1))
                if not (parsed_l and parsed_r):
                    return False

                return self.solver.mkTerm(Kind.MULT, parsed_l, parsed_r)

            case "div":
                parsed_l = self.parse_expression(expressed.named_child(0))
                parsed_r = self.parse_expression(expressed.named_child(1))
                if not (parsed_l and parsed_r):
                    return False

                self.solver.assertFormula(
                    self.solver.mkTerm(Kind.NOT, self.solver.mkTerm(Kind.EQUAL, parsed_r, self.solver.mkReal(0)))
                )

                return self.solver.mkTerm(Kind.DIVISION, parsed_l, parsed_r)

            case "int_div":
                parsed_l = self.parse_expression(expressed.named_child(0))
                parsed_r = self.parse_expression(expressed.named_child(1))
                if not (parsed_l and parsed_r):
                    return False

                int_l = self.solver.mkTerm(Kind.TO_INTEGER, parsed_l)
                int_r = self.solver.mkTerm(Kind.TO_INTEGER, parsed_r)

                self.solver.assertFormula(
                    self.solver.mkTerm(Kind.NOT, self.solver.mkTerm(Kind.EQUAL, int_r, self.solver.mkInteger(0)))
                )

                return self.solver.mkTerm(Kind.INTS_DIVISION, int_l, int_r)

            case "eq":
                return False
                parsed_l = self.parse_expression(expressed.named_child(0))
                parsed_r = self.parse_expression(expressed.named_child(1))
                if not (parsed_l and parsed_r):
                    return False

                return self.solver.mkTerm(Kind.EQUAL, parsed_l, parsed_r)

            case "var":
                return self.get_variable(expressed.text.decode("utf8"))

            case "num":
                number_string = expressed.text.decode("utf8")
                return self.solver.mkReal(float(number_string))

            case _:
                print(f"Overlooked:  {expressed.type}")

        return False

    def parse_tree(self, string):
        tree = self.parser.parse(
            bytes(
                f"{string}",
                "utf8",
            )
        )
        return tree

    def parse_string(self, string):
        tree = self.parser.parse(
            bytes(
                f"{string}",
                "utf8",
            )
        )

        return self.parse_expression(tree.root_node)

    def check(self, a: str, b: str) -> Optional[cvc5.Result]:
        parsed_a = self.parse_string(a)
        if not parsed_a:
            print(f"Parse failure A: {a}")
            return None

        parsed_b = self.parse_string(b)

        if not parsed_b:
            print(f"Parse failure B: {b}")
            return None

        deny_equivalence = self.solver.mkTerm(
            Kind.NOT, self.solver.mkTerm(Kind.EQUAL, parsed_a, parsed_b)
        )

        self.solver.assertFormula(deny_equivalence)
        result = self.solver.checkSat()

        if cvc5.Result.isSat(result):
            model = self.solver.getModel([], self.variable_map.values())

            print(model.decode("utf8"))

        return result


class SimpleTests(unittest.TestCase):
    def test_mul(self):
        checker = EquivalenceChecker()
        result = checker.check("4", "2 * 2")
        assert cvc5.Result.isUnsat(result)

    def test_floor_unit(self):
        checker = EquivalenceChecker()
        result = checker.check("((F * U) * (1/4))", "(F * U) - ((3 * F * U) / 4)")
        assert cvc5.Result.isUnsat(result)

    def test_markup(self):
        checker = EquivalenceChecker()
        result = checker.check("X", "\\frac{2\\text{X}}{2}")
        assert cvc5.Result.isUnsat(result)

    def test_fail(self):
        checker = EquivalenceChecker()
        result = checker.check("4", "2 * X")
        assert cvc5.Result.isSat(result)

    def test_int_div(self):
        checker = EquivalenceChecker()
        result = checker.check("X * (5 // 2)", "2X")
        assert cvc5.Result.isUnsat(result)

    def test_int_div_complex(self):
        checker = EquivalenceChecker()
        result = checker.check(
            "FULL * ((TOTAL + 1) // 2 + 0.6 * (TOTAL // 2))",
            "(FULL * ((TOTAL + 1) // 2) + (3 * FULL / 5) * (TOTAL // 2)",
        )
        assert cvc5.Result.isUnsat(result)

    def test_mixed_frac_a(self):
        checker = EquivalenceChecker()
        result = checker.check("(BOLT + \\frac{BOLT}{2})", "BOLT * 1.5")
        assert cvc5.Result.isUnsat(result)

    @unittest.expectedFailure
    # At present there's an issue with tree-sitter correctly identify dollar signs.
    def test_mixed_frac(self):
        checker = EquivalenceChecker()
        result = checker.check("$BOLT - (BOLT / 2)$", "BOLT * 1.5")
        assert cvc5.Result.isUnsat(result)
