"""Solver framework: base classes, per-solve machinery, and reference solvers."""

from ._bisection import Bisection
from ._interval import Interval
from ._result import SolveResult, SolveStatus
from ._run import SolveRun
from ._solver import BracketingSolver, Solver, StepOutcome
from ._wrapped_function import WrappedFunction
