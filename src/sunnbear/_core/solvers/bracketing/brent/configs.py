"""This module declares the built-in configs of `Brent`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Brent
from .variant import BrentVariant


class BrentConfigsDeclaration(SolverConfigsDeclaration):
    """`BrentConfigsDeclaration` declares the configs of `Brent`, 1 per variant.

    - ``brent[variant='inverse_quadratic']``, the core config: Brent's method, with inverse quadratic interpolation;
    - ``brent[variant='hyperbolic']``, a secondary config: the method of SciPy's ``brenth``, with hyperbolic
      interpolation.

    Section V.g of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles.
    """

    configs = (
        SolverConfig(
            solver_cls=Brent, role=SolverRole.BUILTIN_CORE, solver_kwargs={"variant": BrentVariant.INVERSE_QUADRATIC}
        ),
        SolverConfig(
            solver_cls=Brent, role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": BrentVariant.HYPERBOLIC}
        ),
    )
