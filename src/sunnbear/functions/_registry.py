"""Formula registry: catalog discovery, candidate materialization, reconstruction.

Discovery is a bounded convention: importing this module imports every module
under the catalog package, and defining a `Formula` subclass registers it —
adding a formula is adding a file, with no list to maintain anywhere. `build`
is the reconstruction seam: benchmark workers and users rebuild a
`TestFunction` from its identity plus an externally supplied c-range
(calibration results are explicit inputs; a missing one is an error, never a
default).
"""

import functools
import importlib
import inspect
import pkgutil
from collections.abc import Iterator

from sunnbear.errors import InvalidParamsError, UnknownFormulaError

from . import _formula as _formula_module
from . import catalog
from ._formula import Formula
from ._identity import FunctionId
from ._test_function import CandidateTestFunction, TestFunction


@functools.cache
def _load_catalog() -> None:
    """Import every module under the catalog package (once), registering its formulas.

    Lazy — called from `formulas()` rather than at import time — so importing
    the framework never triggers catalog imports; by the time discovery runs,
    the package is fully initialized and catalog modules can import framework
    names from it without any import-order subtlety. Bounded to the catalog
    package by construction.
    """
    for module_info in pkgutil.walk_packages(catalog.__path__, prefix=f"{catalog.__name__}."):
        importlib.import_module(module_info.name)


# ==================================================================================================
#  Registry API
# ==================================================================================================
def formulas() -> tuple[Formula, ...]:
    """Return one instance of every registered concrete formula, sorted by formula number.

    Raises:
        ValueError: If a registered formula has a non-positive number, or two
            registered formulas share a number.
    """
    _load_catalog()
    # accessed via the module (not imported directly) so the registration list stays
    # a single swap-able seam — e.g. for isolation in downstream test suites
    instances = [cls() for cls in _formula_module.registered_formula_classes if not inspect.isabstract(cls)]
    for formula in instances:
        if formula.number <= 0:
            raise ValueError(f"Formula number must be > 0 (got {formula.number} for {type(formula).__name__}).")
    numbers = [formula.number for formula in instances]
    if len(set(numbers)) != len(numbers):
        raise ValueError("Duplicate formula numbers in registry.")
    return tuple(sorted(instances, key=lambda formula: formula.number))


def candidates(formula: Formula) -> Iterator[CandidateTestFunction]:
    """Materialize a formula's candidates: recipe tuples, deduplicated, validity-filtered.

    Yields candidates in first-seen recipe order; duplicates across recipes
    (exact tuple equality — grid rounding makes equal points bit-identical)
    are emitted once. A formula without recipes yields a single candidate with
    an empty parameter tuple.
    """
    recipes = formula.recipes()
    seen: set[FunctionId] = set()
    param_tuples = (p for recipe in recipes for p in recipe.tuples()) if recipes else iter([()])
    for params in param_tuples:
        fid = FunctionId(formula.number, params)
        # FunctionId equality is notation-blind, so this set is the entire dedup story —
        # cross-recipe duplicates collapse even when spelled in different notations
        if fid in seen or not formula.is_param_tuple_valid(*fid.param_values):
            continue
        seen.add(fid)
        yield formula.candidate(params)


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
    if not formula.is_param_tuple_valid(*fid.param_values):
        raise InvalidParamsError(f"Parameter tuple {fid.params} is invalid for formula {formula.name} (id: {fid}).")
    candidate = formula.candidate(fid.params)
    c_min, c_max = c_range
    return TestFunction(id=candidate.id, fun=candidate.fun, a=candidate.a, b=candidate.b, c_min=c_min, c_max=c_max)
