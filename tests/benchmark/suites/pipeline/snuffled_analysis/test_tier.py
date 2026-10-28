"""`SnuffledTier` builds snuffled's analysis of a test problem at 1 tuple, at the tier's budget and a fixed seed."""

import numpy as np
import pytest
from snuffled import Snuffler

import sunnbear.problems as problems  # Import the module, so that pytest does not collect the `TestProblem` class.
from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, MCSolveSettings, SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SNUFFLED_ANALYSIS_ROOT_SEED, SnuffledTier
from sunnbear._core.problems.core import FormulaRegistry
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls

_MC_SAMPLE_IDX = 5


def _build_problem_and_settings() -> tuple[problems.TestProblem, MCSolveSettings]:
    """Return a test problem with its root at ``c + 1/3`` on [-1, 1], and its settings at the largest tuple set size."""
    define_formula_cls((99, 921), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    problem = FormulaRegistry.candidate_from_id("f99.921").calibrated(c_min=-0.5, c_max=0.5)
    mc_solve_settings = MCSolveSettings.from_test_problem(
        problem, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS, mc_tuples=load_mc_tuples(max(MCTuplesSize))
    )
    return problem, mc_solve_settings


@pytest.mark.parametrize("tier", list(SnuffledTier))
def test_build_snuffler_analyzes_f_at_the_tuple_with_the_tier_budget(isolated_formula_registry, tier):
    """Snuffled finds the root at the tuple's ``c`` with `xtol` as `dx` and the tier's `n_fun_samples` and `n_roots`."""
    # --- arrange ----------------------
    problem, mc_solve_settings = _build_problem_and_settings()

    # --- act --------------------------
    snuffler = tier.build_snuffler(problem, mc_solve_settings=mc_solve_settings, mc_sample_idx=_MC_SAMPLE_IDX)

    # --- assert -----------------------
    function_sampler = snuffler.function_sampler
    assert function_sampler.dx == mc_solve_settings.xtols[_MC_SAMPLE_IDX]
    assert function_sampler.n_fun_samples == tier.n_fun_samples
    assert function_sampler.n_roots == tier.n_roots
    assert [root.x for root in function_sampler.roots] == pytest.approx([mc_solve_settings.cs[_MC_SAMPLE_IDX] + 1 / 3])


def test_build_snuffler_draws_from_the_seed_of_the_problem_and_the_tuple(isolated_formula_registry):
    """The analysis samples f at x-values drawn from `derive_seed`'s seed; another seed draws other x-values."""
    # --- arrange ----------------------
    problem, mc_solve_settings = _build_problem_and_settings()
    seed = (
        derive_seed(
            root_seed=SNUFFLED_ANALYSIS_ROOT_SEED,
            purpose=SeedPurpose.SNUFFLED_ANALYSIS,
            problem_id="f99.921",
            mc_sample_idx=_MC_SAMPLE_IDX,
        )
        % 2**63
    )

    def sample_x_values(seed: int) -> np.ndarray:
        """Return the x-values of an analysis like the one under test, with the given seed."""
        return Snuffler(
            problem.build_x_fun(float(mc_solve_settings.cs[_MC_SAMPLE_IDX])),
            problem.a,
            problem.b,
            dx=float(mc_solve_settings.xtols[_MC_SAMPLE_IDX]),
            seed=seed,
            n_fun_samples=SnuffledTier.LOW.n_fun_samples,
            n_roots=SnuffledTier.LOW.n_roots,
            n_root_samples=SnuffledTier.LOW.n_root_samples,
        ).function_sampler.x_values

    # --- act --------------------------
    snuffler = SnuffledTier.LOW.build_snuffler(
        problem, mc_solve_settings=mc_solve_settings, mc_sample_idx=_MC_SAMPLE_IDX
    )

    # --- assert -----------------------
    assert np.array_equal(snuffler.function_sampler.x_values, sample_x_values(seed))
    assert not np.array_equal(snuffler.function_sampler.x_values, sample_x_values(seed + 1))
