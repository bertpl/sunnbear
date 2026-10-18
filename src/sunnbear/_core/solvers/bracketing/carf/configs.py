"""This module declares the built-in config of `CARF`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import CARF


class CARFConfigs(SolverConfigs):
    """`CARFConfigs` declares the only config of `CARF`, ``carf``, a secondary config, with the paper's constants.

    It is not core because the method is not established yet (published 2026), and `CARF` reconstructs it from the
    paper's description, without the author's code.
    """

    solver_cls = CARF
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
