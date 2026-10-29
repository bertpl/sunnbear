"""snuffled's diagnostics reject a test problem by the same rules in every stage that runs snuffled.

`extract_properties_or_rejection_reason` extracts the requested properties and every diagnostic of 1 analysis, at 1
tuple of the Monte Carlo tuple set, and rejects the test problem by the rules that its docstring lists.
`MAX_ZERO_WIDTH` is the width of the widest region around a root where f is exactly 0.
"""

from collections.abc import Sequence

from snuffled import Diagnostic, Snuffler

from sunnbear._core.benchmark.suites.pipeline.core import RejectionReason

from .function_evaluation_error import FunctionEvaluationError

# snuffled's `MAX_ZERO_WIDTH` is 1 float spacing at a root without an exact 0, and 2 at a root with 1 float where f is
# exactly 0.
#
# At `MAX_BOUND_TO_WIDTH_RATIO`, the largest bound-to-width ratio that validation accepts, `xtol` spans the fewest float
# spacings at the root. At that ratio, this fraction of `xtol` stays well above 2 float spacings, so that a root with 1
# float where f is exactly 0 is not rejected.
MAX_ZERO_WIDTH_IN_XTOL = 1 / 16
# Each flag of snuffled's diagnostics maps to the reason that rejects a test problem when the flag is above 0. The rules
# test the flags in this order, NaN first, because snuffled leaves its other diagnostics unspecified when f returns NaN.
FLAG_REJECTION_REASONS = {
    Diagnostic.NAN_VALUES_DETECTED: RejectionReason.SNUFFLED_NAN_VALUES_DETECTED,
    Diagnostic.INF_VALUES_DETECTED: RejectionReason.SNUFFLED_INF_VALUES_DETECTED,
    Diagnostic.NO_ZEROS_DETECTED: RejectionReason.SNUFFLED_NO_ZEROS_DETECTED,
    Diagnostic.INTERVAL_NOT_BRACKETING_READY: RejectionReason.SNUFFLED_INTERVAL_NOT_BRACKETING_READY,
    Diagnostic.ALL_ROOTS_TOO_CLOSE_TO_EDGE: RejectionReason.SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE,
}


def extract_properties_or_rejection_reason(
    snuffler: Snuffler, properties: Sequence[str], *, xtol: float
) -> dict[str, float] | RejectionReason:
    """Return `properties` from `snuffler`'s analysis, or the reason that its diagnostics reject the test problem.

    The function extracts `properties` first, in their order, then every diagnostic, in the order of `Diagnostic`,
    which puts the NaN and inf flags last, so that those 2 flags also count the NaN and inf values that f returned
    while snuffled computed everything else.

    The function then tests the rules in this order:

    1. f raises;
    2. a flag is above 0, with the flags in the order of `FLAG_REJECTION_REASONS`;
    3. the widest region of exact zeros exceeds `MAX_ZERO_WIDTH_IN_XTOL` times `xtol`.

    Args:
        snuffler: An analysis that `SnuffledAnalysisBudget.build_snuffler` built, which raises `FunctionEvaluationError`
            when f raises.
        properties: The names of snuffled's properties to extract, such as members of `FunctionProperty` and
            `RootProperty`; empty to read only the diagnostics.
        xtol: The `xtol` of the analysis's tuple.

    Returns:
        The value of each of `properties`, keyed by its name, or the `RejectionReason` of the first rule that holds.
    """
    try:
        property_values = {prop: snuffler.extract(prop) for prop in properties}
        diagnostics = {diagnostic: snuffler.extract(diagnostic) for diagnostic in Diagnostic}
    except FunctionEvaluationError:
        return RejectionReason.SNUFFLED_F_RAISES
    for flag, reason in FLAG_REJECTION_REASONS.items():
        if diagnostics[flag] > 0:
            return reason
    if diagnostics[Diagnostic.MAX_ZERO_WIDTH] > MAX_ZERO_WIDTH_IN_XTOL * xtol:
        return RejectionReason.SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE
    else:
        return property_values
