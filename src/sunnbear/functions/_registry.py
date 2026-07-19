"""Formula registry: catalog discovery and reconstruction from an identity.

Discovery is a bounded convention: the first registry call imports every
module under the catalog package, and defining a `Formula` subclass registers
it — adding a formula is adding a file, with no list to maintain anywhere.
`FormulaRegistry.candidate_from_id` is the reconstruction seam: benchmark
workers and users rebuild a test function from its identity, then attach the
calibrated c-range a suite artifact supplies
(`CandidateTestFunction.calibrated`) — a missing c-range is an error, never a
default.
"""

import functools
import importlib
import inspect
import pkgutil

from sunnbear.errors import InvalidParamsError, UnknownFormulaError

from . import _formula as _formula_module
from . import catalog
from ._formula import Formula
from ._identity import FunctionId
from ._test_function import CandidateTestFunction


@functools.cache
def _load_catalog() -> None:
    """Import every module under the catalog package (once), registering its formulas.

    Lazy — called from `FormulaRegistry.formulas` rather than at import time — so importing
    the framework never triggers catalog imports; by the time discovery runs,
    the package is fully initialized and catalog modules can import framework
    names from it without any import-order subtlety. Bounded to the catalog
    package by construction.
    """
    for module_info in pkgutil.walk_packages(catalog.__path__, prefix=f"{catalog.__name__}."):
        importlib.import_module(module_info.name)


# ==================================================================================================
#  FormulaRegistry
# ==================================================================================================
class FormulaRegistry:
    """The catalog's formulas: enumerate them, or rebuild one candidate from an identity.

    Accessors only — there is no instance state to carry, since the registry is
    just the set of `Formula` subclasses discovered under the catalog package.
    """

    @classmethod
    def formulas(cls) -> tuple[Formula, ...]:
        """Return one instance of every registered concrete formula, sorted by formula number.

        Raises:
            ValueError: If a registered formula has a non-positive number, or two
                registered formulas share a number.
        """
        _load_catalog()
        # accessed via the module (not imported directly) so the registration list stays
        # a single swap-able seam — e.g. for isolation in downstream test suites
        instances = [
            formula_cls()
            for formula_cls in _formula_module.registered_formula_classes
            if not inspect.isabstract(formula_cls)
        ]
        for formula in instances:
            if formula.number <= 0:
                raise ValueError(f"Formula number must be > 0 (got {formula.number} for {type(formula).__name__}).")
        numbers = [formula.number for formula in instances]
        if len(set(numbers)) != len(numbers):
            raise ValueError("Duplicate formula numbers in registry.")
        return tuple(sorted(instances, key=lambda formula: formula.number))

    @classmethod
    def candidate_from_id(cls, function_id: FunctionId | str) -> CandidateTestFunction:
        """Reconstruct a candidate test function from its identity.

        Attach a calibrated c-range via `CandidateTestFunction.calibrated` to
        obtain a benchmarkable `TestFunction`.

        Args:
            function_id: The identity, as object or canonical string.

        Raises:
            UnknownFormulaError: If the formula number is not in the registry.
            InvalidParamsError: If the parameter tuple fails the formula's validity criteria.
        """
        fid = FunctionId.from_string(function_id) if isinstance(function_id, str) else function_id
        by_number = {formula.number: formula for formula in cls.formulas()}
        formula = by_number.get(fid.formula)
        if formula is None:
            raise UnknownFormulaError(f"No registered formula with number {fid.formula} (id: {fid}).")
        if not formula.is_param_tuple_valid(*fid.param_values):
            raise InvalidParamsError(f"Parameter tuple {fid.params} is invalid for formula {formula.name} (id: {fid}).")
        return formula.build_candidate(fid.params)
