"""This package holds the shipped formulas: concrete `Formula` subclasses, one module per formula.

Layout convention: one subpackage per number block (e.g. ``f1xx_polynomials``),
one module per formula number (e.g. ``f101_cubic``), one `Formula` subclass
per module.

Every subpackage is imported here, and every module is imported in its own
subpackage, so importing this package registers every shipped formula.
"""

from . import f1xx_polynomials
