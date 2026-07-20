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
from sunnbear.functions import (
    CandidateTestFunction,
    Formula,
    FormulaRegistry,
    FunctionId,
    ParamRecipe,
    TestFunction,
)
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
