"""This module collects every exception sunnbear raises, in one import location.

All derive from `SunnbearError`; each is defined in the layer that raises it and re-exported here.
"""

from ._core.data.exceptions import ArtifactError
from ._core.exceptions import SunnbearError
from ._core.functions.core.exceptions import FormulaTaxonomyError, InvalidParamsError, UnknownFormulaError
from ._core.solvers.core.exceptions import (
    DivergedError,
    FunctionDomainError,
    MaxFevalsExceeded,
    SolveException,
    UnknownSolverConfigError,
)

__all__ = [
    "ArtifactError",
    "DivergedError",
    "FormulaTaxonomyError",
    "FunctionDomainError",
    "InvalidParamsError",
    "MaxFevalsExceeded",
    "SolveException",
    "SunnbearError",
    "UnknownFormulaError",
    "UnknownSolverConfigError",
]
