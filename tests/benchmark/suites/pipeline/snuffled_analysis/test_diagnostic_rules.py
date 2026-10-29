"""`extract_properties_or_rejection_reason` returns the requested properties of an analysis that its diagnostics pass,
and the flags of the rules cover every diagnostic of snuffled except the zero width.

The rules themselves are tested through validation's snuffled diagnostics check, 1 test problem per rule.
"""

from snuffled import Diagnostic, FunctionProperty, RootProperty

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, MCSolveSettings
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import (
    FLAG_REJECTION_REASONS,
    SnuffledAnalysisBudget,
    extract_properties_or_rejection_reason,
)
from sunnbear._core.problems.core import FormulaRegistry
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


def test_an_analysis_that_passes_returns_the_requested_properties(isolated_formula_registry):
    """For a test problem with 1 simple root, the result holds a value in [0, 1] for each requested property."""
    # --- arrange ----------------------
    define_formula_cls((99, 941), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    problem = FormulaRegistry.candidate_from_id("f99.941").calibrated(c_min=-0.5, c_max=0.5)
    mc_solve_settings = MCSolveSettings.from_test_problem(
        problem, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS, mc_tuples=load_mc_tuples(MCTuplesSize.SIZE_32)
    )
    snuffler = SnuffledAnalysisBudget.LOW.build_snuffler(problem, mc_solve_settings=mc_solve_settings, mc_sample_idx=0)
    properties = [*RootProperty, *FunctionProperty]

    # --- act --------------------------
    result = extract_properties_or_rejection_reason(snuffler, properties, xtol=float(mc_solve_settings.xtols[0]))

    # --- assert -----------------------
    assert isinstance(result, dict)
    assert list(result) == properties
    assert all(0.0 <= value <= 1.0 for value in result.values())


def test_the_flags_cover_every_diagnostic_except_the_max_zero_width():
    """`FLAG_REJECTION_REASONS` maps every diagnostic of snuffled except `MAX_ZERO_WIDTH` to a reason."""
    # --- act / assert -----------------
    assert set(FLAG_REJECTION_REASONS) == set(Diagnostic) - {Diagnostic.MAX_ZERO_WIDTH}
