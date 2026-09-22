"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` from the solver core.

Each solver is a package of its own, so a solver with helper modules keeps them beside its solver module.
"""

from .bisection import Bisection
from .regula_falsi import RegulaFalsi
