"""This package holds the bracketing solvers, each a subclass of `BracketingSolver` from the solver core.

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
from .illinois import Illinois
from .regula_falsi import RegulaFalsi
