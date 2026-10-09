"""This module declares the built-in configs of `CARF`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import CARF


class CARFConfig(SolverConfig):
    """`CARFConfig` is a secondary config, with the paper's constants.

    It is not core because the method is recent, and `CARF` reconstructs it from the paper's description, without the
    author's code.
    """

    solver_cls = CARF
    role = SolverRole.BUILTIN_SECONDARY
