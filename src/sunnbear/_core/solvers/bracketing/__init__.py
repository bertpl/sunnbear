"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` from the solver core.

Each solver is a package of its own, holding its solver module, its built-in configs, and any helper
modules. Importing this package registers the built-in configs.

Each solver class holds its whole algorithm, even where 2 solvers differ in a single detail, as regula falsi and
the Illinois method do in the function value that they use at the retained bound. The benchmark counts every
solver's flops, and a base class shared by such a family would add branches, and possibly flops, that the
published algorithms do not have; a self-contained class reads as its published algorithm. Variants of 1
algorithm, such as values of 1 of its parameters, are configs of 1 class.
"""

from .bisection import Bisection
from .illinois import Illinois
from .regula_falsi import RegulaFalsi
