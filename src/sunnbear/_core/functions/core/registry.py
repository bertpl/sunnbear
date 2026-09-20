"""The formula registry holds the registered formulas and reconstructs one from an identity.

Defining a `Formula` subclass registers it; the registry reads that list and
never imports anything, so the shipped formulas must be imported before the
registry is first read, and the test-function package imports them on import.

`FormulaRegistry.candidate_from_id` is the reconstruction seam: benchmark
workers and users rebuild a test function from its identity, then attach the
calibrated c-range a suite artifact supplies
(`CandidateTestFunction.calibrated`) — a missing c-range is an error, never a
default.
"""

import inspect
from typing import ClassVar

from . import formula as formula_module
from .exceptions import InvalidParamsError, UnknownFormulaError
from .formula import Formula
from .identity import FunctionId
from .test_function import CandidateTestFunction


# ==================================================================================================
#  FormulaRegistry
# ==================================================================================================
class FormulaRegistry:
    """`FormulaRegistry` enumerates the registered formulas, or rebuilds one candidate from an identity.

    State is a lazily-populated class-level snapshot of the registered
    formulas, taken on the first accessor call (`_ensure_registry_populated`).
    Defining formulas after that snapshot is unsupported; a deliberate
    user-extension mechanism (explicit registration, invalidation) can be added
    later without changing this seam.
    """

    _formulas: ClassVar[tuple[Formula, ...] | None] = None
    _formulas_by_number: ClassVar[dict[int, Formula] | None] = None

    @classmethod
    def _ensure_registry_populated(cls) -> tuple[tuple[Formula, ...], dict[int, Formula]]:
        """Populate the snapshot — instantiation, validation, index — once.

        Returns the snapshot (formulas, by-number index), so callers consume
        the population result directly and never re-read the class fields.
        The fields are assigned only after every check has passed, so a
        validation failure leaves the registry unpopulated and re-raises on
        every subsequent call instead of caching a half-built state.

        Raises:
            ValueError: If a registered formula has a non-positive number, or
                two registered formulas share a number.
        """
        if cls._formulas is not None and cls._formulas_by_number is not None:
            return cls._formulas, cls._formulas_by_number
        # accessed via the module (not imported directly) so the registration list stays
        # a single swap-able seam — e.g. for isolation in downstream test suites
        instances = [
            formula_cls()
            for formula_cls in formula_module.registered_formula_classes
            if not inspect.isabstract(formula_cls)
        ]
        for formula in instances:
            if formula.number <= 0:
                raise ValueError(f"Formula number must be > 0 (got {formula.number} for {type(formula).__name__}).")
        numbers = [formula.number for formula in instances]
        if len(set(numbers)) != len(numbers):
            raise ValueError("Duplicate formula numbers in registry.")
        formulas = tuple(sorted(instances, key=lambda formula: formula.number))
        by_number = {formula.number: formula for formula in formulas}
        cls._formulas, cls._formulas_by_number = formulas, by_number
        return formulas, by_number

    @classmethod
    def formulas(cls) -> tuple[Formula, ...]:
        """Return one instance of every registered concrete formula, sorted by formula number.

        Raises:
            ValueError: If a registered formula has a non-positive number, or two
                registered formulas share a number.
        """
        formulas, _ = cls._ensure_registry_populated()
        return formulas

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
        _, by_number = cls._ensure_registry_populated()
        formula = by_number.get(fid.formula)
        if formula is None:
            raise UnknownFormulaError(f"No registered formula with number {fid.formula} (id: {fid}).")
        if not formula.is_param_tuple_valid(*fid.param_values):
            raise InvalidParamsError(f"Parameter tuple {fid.params} is invalid for formula {formula.name} (id: {fid}).")
        return formula.build_candidate(fid.params)
