"""`sunnbear` is a benchmarking framework for univariate root-solvers.

A solver author subclasses `Solver` or `BracketingSolver`; a formula author
subclasses `Formula`. The reference solvers live in `sunnbear.solvers`,
summary statistics in `sunnbear.stats`.
"""

from .errors import MaxFevalsExceeded
from .functions import Formula, FormulaRegistry, FunctionId, ParamRecipe, TestFunction
from .solvers import BracketingSolver, Interval, Solver, SolveResult, SolveRun, SolveStatus

__all__ = [
    "BracketingSolver",
    "Formula",
    "FormulaRegistry",
    "FunctionId",
    "Interval",
    "MaxFevalsExceeded",
    "ParamRecipe",
    "SolveResult",
    "SolveRun",
    "SolveStatus",
    "Solver",
    "TestFunction",
]
