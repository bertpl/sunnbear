"""The formula registry holds the registered formulas and reconstructs one from an identity.

Defining a concrete `Formula` subclass registers one instance of it here, and every check runs at
that moment, so a malformed formula fails when its module is imported, never inside a benchmark
worker.

The registry itself imports nothing: the shipped formulas are registered when the
test-function package imports the formula catalog.

`FormulaRegistry.candidate_from_id` is the reconstruction seam: benchmark
workers and users rebuild a test function from its identity, then attach the
calibrated c-range a suite artifact supplies
(`CandidateTestFunction.calibrated`) — a missing c-range is an error, never a
default.
"""

from typing import TYPE_CHECKING, ClassVar

from .exceptions import InvalidParamsError, UnknownFormulaError
from .identity import FunctionId
from .test_function import CandidateTestFunction

if TYPE_CHECKING:  # type-only: formula imports this module at runtime, so a runtime import here would be circular
    from .formula import Formula


# ==================================================================================================
#  FormulaRegistry
# ==================================================================================================
class FormulaRegistry:
    """`FormulaRegistry` enumerates the registered formulas, or rebuilds one candidate from an identity.

    `Formula.__init_subclass__` calls `register` for every concrete subclass, so the registry is
    complete as soon as the formula modules are imported; nothing is discovered lazily.
    """

    _formulas_by_number: ClassVar[dict[int, "Formula"]] = {}

    @classmethod
    def register(cls, formula_cls: "type[Formula]") -> None:
        """Instantiate a concrete formula class and register it under its number.

        Called from `Formula.__init_subclass__` for every concrete subclass, so a failing check
        surfaces at class definition.

        Raises:
            ValueError: If the formula's number is not positive, or another registered formula has
                the same number.
        """
        formula = formula_cls()
        if formula.number <= 0:
            raise ValueError(f"Formula number must be > 0 (got {formula.number} for {formula_cls.__name__}).")
        if formula.number in cls._formulas_by_number:
            existing_name = type(cls._formulas_by_number[formula.number]).__name__
            raise ValueError(f"Duplicate formula number {formula.number}: {formula_cls.__name__} and {existing_name}.")
        cls._formulas_by_number[formula.number] = formula

    @classmethod
    def formulas(cls) -> "tuple[Formula, ...]":
        """Return one instance of every registered concrete formula, sorted by formula number."""
        return tuple(sorted(cls._formulas_by_number.values(), key=lambda formula: formula.number))

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
        formula = cls._formulas_by_number.get(fid.formula)
        if formula is None:
            raise UnknownFormulaError(f"No registered formula with number {fid.formula} (id: {fid}).")
        if not formula.is_param_tuple_valid(*fid.param_values):
            raise InvalidParamsError(f"Parameter tuple {fid.params} is invalid for formula {formula.name} (id: {fid}).")
        return formula.build_candidate(fid.params)
