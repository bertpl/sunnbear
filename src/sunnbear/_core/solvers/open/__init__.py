"""This package holds the open solvers, each a subclass of `Solver` from the solver core.

An open solver does not keep an interval around the root: each iterate depends only on earlier iterates, so iterates
may leave the initial interval, and the solve's result is not guaranteed to lie within ``xtol`` of a root. `Solver`
records a solve that leaves the initial interval as ``DIVERGED``; `SolveStatus` lists the cases.

Each solver is a package of its own, holding its solver module and its built-in configs. Importing this package
registers the built-in configs.
"""

from .secant import Secant
