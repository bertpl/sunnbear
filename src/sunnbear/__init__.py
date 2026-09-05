"""`sunnbear` is a benchmarking framework for univariate root-solvers.

A solver author subclasses `Solver` or `BracketingSolver`; a formula author
subclasses `Formula`. The other names exported here are what those classes
hand you, documented there. The reference solvers live in `sunnbear.solvers`,
summary statistics in `sunnbear.stats`.
"""

from sunnbear.errors import MaxFevalsExceeded
from sunnbear.functions import Formula, FormulaRegistry, FunctionId, ParamRecipe, TestFunction
from sunnbear.solvers import BracketingSolver, Interval, Solver, SolveResult, SolveRun, SolveStatus

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
