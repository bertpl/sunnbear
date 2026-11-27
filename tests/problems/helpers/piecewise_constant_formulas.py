"""`PIECEWISE_CONSTANT_FORMULA_NUMBERS` lists the shipped formulas whose functions are constant between their jumps.

`follows_effect_of_c` cannot judge such a function by its derivatives, so the catalog's test of how a formula applies
``c`` skips these formulas, and the tests of their family check instead where ``c`` moves their jumps. Each of those 2
test modules asserts that its own set of formulas equals this one.
"""

PIECEWISE_CONSTANT_FORMULA_NUMBERS = frozenset({(2, 7, 1), (2, 7, 2), (2, 7, 4)})
