"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` or `Solver` from the solver core.

A solver whose iteration evaluates 1 point and splits the interval there subclasses `BracketingSolver`, which owns
the iteration loop and the stopping criterion. A solver whose iteration evaluates more than once, or whose stopping
criterion is its own, subclasses `Solver` and writes its own loop.

Each solver is a package of its own, holding its solver module, its built-in configs, and any helper
modules. Importing this package registers the built-in configs.

The implementation principles in ``IMPLEMENTATION_PRINCIPLES.md`` of the parent package say how each solver
implements its published method, including why each solver class holds its whole algorithm and computes each formula
in its source's form.
"""

from .anderson_bjorck import AndersonBjorck
from .bisection import Bisection
from .brent import Brent
from .carf import CARF
from .chandrupatla import Chandrupatla
from .illinois import Illinois
from .itp import ITP, ITPVariant
from .modab import ModAB
from .pegasus import Pegasus
from .regula_falsi import RegulaFalsi
from .ridders import Ridders, RiddersVariant
from .steffen_brent import SteffenBrent
from .toms748 import TOMS748
