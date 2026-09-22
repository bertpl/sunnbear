"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` from the solver core.

Each solver is a package of its own, holding its solver module, its built-in configs, and any helper
modules. Importing this package registers the built-in configs.
"""

from .bisection import Bisection, BisectionConfig
from .regula_falsi import RegulaFalsi, RegulaFalsiConfig
