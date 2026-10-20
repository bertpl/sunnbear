"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` or `Solver` from the solver core.

A solver whose iteration evaluates 1 x-value and splits the interval there subclasses `BracketingSolver`, which owns
the iteration loop and the stopping criterion. Any other solver subclasses `Solver` and writes its own loop; the
docstring of `BracketingSolver` lists when that applies.

Each solver is a package of its own, holding its solver module, its built-in configs, and any helper
modules. Importing this package registers the built-in configs.

``SOLVER_IMPLEMENTATIONS.md`` in the parent package states the solvers' shared implementation choices, and why
each solver class holds its whole algorithm.
"""

from .anderson_bjorck import AndersonBjorck
from .bisection import Bisection
from .brent import Brent, BrentVariant
from .carf import CARF
from .chandrupatla import Chandrupatla
from .ellithy import Ellithy, EllithyVariant
from .ford import Ford, FordVariant
from .illinois import Illinois
from .itp import ITP, ITPVariant
from .modab import ModAB, ModABSafeguarded
from .pegasus import Pegasus
from .regula_falsi import RegulaFalsi
from .ridders import Ridders, RiddersVariant
from .steffen_brent import SteffenBrent
from .toms748 import TOMS748
