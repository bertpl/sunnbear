"""This module collects every exception that sunnbear's public API raises, in one import location.

All derive from `SunnbearError`; each is defined in the layer that raises it and re-exported here.
"""

from ._core.artifacts.exceptions import ArtifactError
from ._core.benchmark.runner.exceptions import BenchmarkRunError
from ._core.exceptions import SunnbearError
from ._core.solvers.core.exceptions import (
    DivergedError,
    FunctionDomainError,
    MaxFevalsExceeded,
    SolveException,
    UnknownSolverConfigError,
)

__all__ = [
    "ArtifactError",
    "BenchmarkRunError",
    "DivergedError",
    "FunctionDomainError",
    "MaxFevalsExceeded",
    "SolveException",
    "SunnbearError",
    "UnknownSolverConfigError",
]
