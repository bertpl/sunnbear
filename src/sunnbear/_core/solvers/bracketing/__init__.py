"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` or `Solver` from the solver core.

A solver whose iteration evaluates 1 point and splits the interval there subclasses `BracketingSolver`, which owns
the iteration loop and the stopping criterion. A solver whose iteration evaluates more than once, or whose stopping
criterion is its own, subclasses `Solver` and writes its own loop.

Each solver is a package of its own, holding its solver module, its built-in configs, and any helper
modules. Importing this package registers the built-in configs.

Each solver class holds its whole algorithm, even where 2 solvers differ in a single detail, as `RegulaFalsi` and
`Illinois` do, for 2 reasons:

- the benchmark counts every solver's flops, and a base class shared by such a family would add branches, and
  possibly flops, that the published algorithms do not have;
- a reader can compare a self-contained class with its published algorithm step by step.

Variants of one algorithm, such as different values of one of its parameters, are configs of a single class.
"""

from .bisection import Bisection
from .brent import Brent
from .illinois import Illinois
from .regula_falsi import RegulaFalsi
from .ridders import Ridders, RiddersVariant
