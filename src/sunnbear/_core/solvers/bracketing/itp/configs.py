"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import ITP
from .variant import ITPVariant


class ITPConfigsDeclaration(SolverConfigsDeclaration):
    """`ITPConfigsDeclaration` declares the configs of `ITP`, which differ in projection radius and in ``n_slack``.

    - ``itp[n_slack=0,variant='paper_experiments']``, the core config: the settings of the paper's experiments and of
      the authors' code;
    - ``itp[n_slack=0,variant='paper_pseudocode']``, a secondary config: the projection radius of the paper's
      pseudocode;
    - ``itp[n_slack=4,variant='paper_experiments']``, a secondary config: the core config with 4 iterations of slack.

    Section V.c of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles, and for ``n_slack = 4``.
    """

    configs = (
        SolverConfig(
            solver_cls=ITP,
            role=SolverRole.BUILTIN_CORE,
            solver_kwargs={"n_slack": 0, "variant": ITPVariant.PAPER_EXPERIMENTS},
            readable_name="ITP (modified, n₀=0)",
            summary=(
                "The ITP method of Oliveira and Takahashi (2020), with $n_0 = 0$ and the numerical tolerance "
                "measure of the authors' code for the article's experiments, which lowers the projection radius "
                r"$r$ to $\max(0.99 \cdot r - x_{\text{tol}}/2, 0)$."
            ),
        ),
        SolverConfig(
            solver_cls=ITP,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"n_slack": 0, "variant": ITPVariant.PAPER_PSEUDOCODE},
            readable_name="ITP (n₀=0)",
            summary=(
                "The ITP method of Oliveira and Takahashi (2020), as the pseudocode of the article's Appendix B "
                "states it, with $n_0 = 0$: in exact arithmetic, at most as many iterations as bisection."
            ),
        ),
        SolverConfig(
            solver_cls=ITP,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"n_slack": 4, "variant": ITPVariant.PAPER_EXPERIMENTS},
            readable_name="ITP (modified, n₀=4)",
            summary=(
                "The ITP method of Oliveira and Takahashi (2020), with $n_0 = 4$, up to 4 iterations more than "
                "bisection in exact arithmetic, and the numerical tolerance measure of the authors' code for the "
                r"article's experiments, which lowers the projection radius $r$ to $\max(0.99 \cdot r - "
                r"x_{\text{tol}}/2, 0)$."
            ),
        ),
    )
