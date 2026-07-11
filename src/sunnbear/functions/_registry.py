"""Explicit formula registry: aggregation, candidate materialization, reconstruction.

Formulas register by appearing in a module-level ``FORMULAS`` tuple that this
module imports and aggregates explicitly — no reflection, no import side
effects. `build` is the reconstruction seam: benchmark workers and users
rebuild a `TestFunction` from its identity plus an externally supplied
c-range (calibration results are explicit inputs; a missing one is an error,
never a default).
"""

from collections.abc import Iterator

from sunnbear.errors import InvalidParamsError, UnknownFormulaError

from ._formula import Formula
from ._identity import FunctionId
from ._test_function import Candidate, TestFunction
from .examples import FORMULAS as _EXAMPLE_FORMULAS

# Explicit aggregation, one entry per formula module.
_ALL_FORMULAS: tuple[Formula, ...] = (*_EXAMPLE_FORMULAS,)


# ==================================================================================================
#  Registry API
# ==================================================================================================
def formulas() -> tuple[Formula, ...]:
    """Return all registered formulas, sorted by formula number.

    Raises:
        ValueError: If two registered formulas share a number.
    """
    numbers = [formula.number for formula in _ALL_FORMULAS]
    if len(set(numbers)) != len(numbers):
        raise ValueError("Duplicate formula numbers in registry.")
    return tuple(sorted(_ALL_FORMULAS, key=lambda formula: formula.number))


def candidates(formula: Formula) -> Iterator[Candidate]:
    """Materialize a formula's candidates: recipe tuples, deduplicated, validity-filtered.

    Yields candidates in first-seen recipe order; duplicates across recipes
    (exact tuple equality — grid rounding makes equal points bit-identical)
    are emitted once. A formula without recipes yields a single candidate with
    an empty parameter tuple.
    """
    seen: set[tuple[float, ...]] = set()
    param_tuples = (p for recipe in formula.recipes for p in recipe.tuples()) if formula.recipes else iter([()])
    for params in param_tuples:
        if params in seen or not formula.is_param_tuple_valid(*params):
            continue
        seen.add(params)
        a, b = formula.bracket(*params)
        yield Candidate(id=FunctionId(formula.number, params), fun=formula.make(*params), a=a, b=b)


def build(function_id: FunctionId | str, c_range: tuple[float, float]) -> TestFunction:
    """Reconstruct a `TestFunction` from its identity and an externally supplied c-range.

    Args:
        function_id: The identity, as object or canonical string.
        c_range: The calibrated ``(c_min, c_max)`` for this function.

    Raises:
        UnknownFormulaError: If the formula number is not in the registry.
        InvalidParamsError: If the parameter tuple fails the formula's validity criteria.
    """
    fid = FunctionId.from_string(function_id) if isinstance(function_id, str) else function_id
    by_number = {formula.number: formula for formula in formulas()}
    formula = by_number.get(fid.formula)
    if formula is None:
        raise UnknownFormulaError(f"No registered formula with number {fid.formula} (id: {fid}).")
    if not formula.is_param_tuple_valid(*fid.params):
        raise InvalidParamsError(f"Parameter tuple {fid.params} is invalid for formula {formula.name} (id: {fid}).")
    a, b = formula.bracket(*fid.params)
    c_min, c_max = c_range
    return TestFunction(id=fid, fun=formula.make(*fid.params), a=a, b=b, c_min=c_min, c_max=c_max)
