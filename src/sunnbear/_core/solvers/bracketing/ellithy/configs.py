"""This module declares the built-in configs of `Ellithy`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Ellithy
from .variant import EllithyVariant


class EllithyConfigsDeclaration(SolverConfigsDeclaration):
    """`EllithyConfigsDeclaration` declares the configs of `Ellithy`, 1 per variant.

    - ``ellithy[variant='bf']``, a secondary config: Opt.BF of Ellithy (2026), bisection and false position;
    - ``ellithy[variant='bfms']``, a secondary config: Opt.BFMS of Ellithy (2026), bisection, false position and a
      modified-secant step;
    - ``ellithy[variant='tf']``, a secondary config: Opt.TF of Ellithy (2026), trisection and false position;
    - ``ellithy[variant='tfms']``, a secondary config: Opt.TFMS of Ellithy (2026), trisection, false position and a
      modified-secant step.

    Section V.f of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles.
    """

    solver_cls = Ellithy
    configs = (
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": EllithyVariant.BF}),
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": EllithyVariant.BFMS}),
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": EllithyVariant.TF}),
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": EllithyVariant.TFMS}),
    )
