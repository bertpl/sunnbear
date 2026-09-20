"""This module collects every exception sunnbear raises, in one import location.

All derive from `SunnbearError`; each is defined in the layer that raises it and re-exported here.
"""

from sunnbear._core.exceptions import SunnbearError
from sunnbear._core.functions.core.exceptions import InvalidParamsError, UnknownFormulaError
from sunnbear._core.solvers.core.exceptions import (
    DivergedError,
    FunctionDomainError,
    MaxFevalsExceeded,
    SolveInterrupt,
)

__all__ = [
    "DivergedError",
    "FunctionDomainError",
    "InvalidParamsError",
    "MaxFevalsExceeded",
    "SolveInterrupt",
    "SunnbearError",
    "UnknownFormulaError",
]
