"""Benchmarking framework for univariate root-solvers — under construction."""

from sunnbear.errors import (
    DivergedError,
    FunctionDomainError,
    InvalidParamsError,
    MaxFevalsExceeded,
    SolveInterrupt,
    SunnbearError,
    UnknownFormulaError,
)
from sunnbear.functions import Candidate, Formula, FunctionId, ParamRecipe, TestFunction, build, candidates, formulas
from sunnbear.solvers import (
    Bisection,
    BracketingSolver,
    Interval,
    RegulaFalsi,
    Solver,
    SolveResult,
    SolveRun,
    SolveStatus,
    StepOutcome,
)
