"""The formula registry holds the registered formulas and categories, and rebuilds a candidate from an identity.

Defining a concrete `Formula` or a `FormulaCategory` subclass registers one instance of it here.
Checks run in 2 stages:

- **At class definition**, every check that concerns the node alone: a valid number, and no other
  registered node with the same number. A malformed formula fails when its module is imported.
- **On the first read** of the registry, and again after any later registration, the checks across
  nodes: every node's parent category exists, no category holds both subcategories and formulas,
  and no node outside sunnbear sits under a built-in-only top-level category. These cannot run
  at class definition, because a category's package imports its formula modules at the top of
  its ``__init__.py``, so its formulas register before the category itself.

The registry itself imports nothing: the shipped formulas are registered when the
test-function package imports the formula catalog.

`FormulaRegistry.candidate_from_id` rebuilds a candidate test function from its identity, for
benchmark workers and users; the calibrated c-range that a suite artifact supplies is then
attached with `CandidateTestFunction.calibrated`. A missing c-range is an error, never a default.
"""

from typing import TYPE_CHECKING, ClassVar

from sunnbear._core.builtin import is_defined_in_sunnbear

from .exceptions import FormulaTaxonomyError, InvalidParamsError, UnknownFormulaError
from .identity import FunctionId
from .taxonomy import TaxonomyNode, format_number
from .test_function import CandidateTestFunction

# type-only: formula and category import this module at runtime, so a runtime import would be circular
if TYPE_CHECKING:
    from .category import FormulaCategory
    from .formula import Formula


# ==================================================================================================
#  FormulaRegistry
# ==================================================================================================
class FormulaRegistry:
    """`FormulaRegistry` enumerates the registered formulas and categories, or rebuilds one candidate from an identity.

    `Formula.__init_subclass__` and `FormulaCategory.__init_subclass__` call `register_formula` and
    `register_category`, so the registry is complete as soon as the modules that define them are imported.
    Every public read first checks the taxonomy tree, if a registration happened since the last check.
    """

    _formulas_by_number: ClassVar[dict[tuple[int, ...], "Formula"]] = {}
    _categories_by_number: ClassVar[dict[tuple[int, ...], "FormulaCategory"]] = {}
    _is_taxonomy_validated: ClassVar[bool] = False

    # --------------------------------------------------------------------------
    #  Registration
    # --------------------------------------------------------------------------
    @classmethod
    def register_formula(cls, formula_cls: "type[Formula]") -> None:
        """Instantiate a concrete formula class and register it under its number.

        Raises:
            ValueError: If another registered formula or category has the same number.
        """
        formula = formula_cls()
        cls._check_number_is_free(formula)
        cls._formulas_by_number[formula.number] = formula
        cls._is_taxonomy_validated = False

    @classmethod
    def register_category(cls, category_cls: "type[FormulaCategory]") -> None:
        """Instantiate a category class and register it under its number.

        Raises:
            ValueError: If another registered formula or category has the same number.
        """
        category = category_cls()
        cls._check_number_is_free(category)
        cls._categories_by_number[category.number] = category
        cls._is_taxonomy_validated = False

    # --------------------------------------------------------------------------
    #  Reads
    # --------------------------------------------------------------------------
    @classmethod
    def formulas(cls) -> "tuple[Formula, ...]":
        """Return one instance of every registered concrete formula, sorted by number.

        Raises:
            FormulaTaxonomyError: If the registered nodes do not form a valid taxonomy tree.
        """
        cls._ensure_taxonomy_validated()
        return tuple(formula for _, formula in sorted(cls._formulas_by_number.items()))

    @classmethod
    def categories(cls) -> "tuple[FormulaCategory, ...]":
        """Return one instance of every registered category, sorted by number, so each follows its parent.

        Raises:
            FormulaTaxonomyError: If the registered nodes do not form a valid taxonomy tree.
        """
        cls._ensure_taxonomy_validated()
        return tuple(category for _, category in sorted(cls._categories_by_number.items()))

    @classmethod
    def candidate_from_id(cls, function_id: FunctionId | str) -> CandidateTestFunction:
        """Reconstruct a candidate test function from its identity.

        Attach a calibrated c-range via `CandidateTestFunction.calibrated` to
        obtain a benchmarkable `TestFunction`.

        Args:
            function_id: The identity, as object or canonical string.

        Raises:
            FormulaTaxonomyError: If the registered nodes do not form a valid taxonomy tree.
            UnknownFormulaError: If the formula number is not in the registry.
            InvalidParamsError: If the parameter tuple fails the formula's validity criteria.
        """
        cls._ensure_taxonomy_validated()
        fid = FunctionId.from_string(function_id) if isinstance(function_id, str) else function_id
        formula = cls._formulas_by_number.get(fid.formula_number)
        if formula is None:
            raise UnknownFormulaError(
                f"No registered formula with number {format_number(fid.formula_number)} (id: {fid})."
            )
        if not formula.is_param_tuple_valid(*fid.param_values):
            raise InvalidParamsError(f"Parameter tuple {fid.params} is invalid for formula {formula.name} (id: {fid}).")
        return formula.build_candidate(fid.params)

    # --------------------------------------------------------------------------
    #  Taxonomy checks
    # --------------------------------------------------------------------------
    @classmethod
    def _check_number_is_free(cls, node: TaxonomyNode) -> None:
        """Check that no registered formula or category has the number of `node`.

        Raises:
            ValueError: If one does.
        """
        existing = cls._formulas_by_number.get(node.number) or cls._categories_by_number.get(node.number)
        if existing is not None:
            raise ValueError(
                f"Duplicate taxonomy number {format_number(node.number)}: "
                f"{type(node).__name__} and {type(existing).__name__}."
            )

    @classmethod
    def _ensure_taxonomy_validated(cls) -> None:
        """Run `_validate_taxonomy` unless it has passed since the last registration."""
        if not cls._is_taxonomy_validated:
            cls._validate_taxonomy()
            cls._is_taxonomy_validated = True

    @classmethod
    def _validate_taxonomy(cls) -> None:
        """Check that the registered formulas and categories form a valid taxonomy tree.

        Raises:
            FormulaTaxonomyError: If a node's parent category is not registered, a category holds
                both subcategories and formulas, or a node defined outside sunnbear sits under a
                built-in-only top-level category.
        """
        categories = cls._categories_by_number
        nodes: list[TaxonomyNode] = [*categories.values(), *cls._formulas_by_number.values()]

        # --- every parent exists ------------------------
        # a formula's number has at least 2 elements, so only a top-level category has no parent
        for node in nodes:
            parent_number = node.number[:-1]
            if parent_number and parent_number not in categories:
                raise FormulaTaxonomyError(
                    f"{type(node).__name__} ({format_number(node.number)}) has no registered parent "
                    f"category {format_number(parent_number)}."
                )

        # --- no mixed categories ------------------------
        parents_of_formulas = {number[:-1] for number in cls._formulas_by_number}
        parents_of_categories = {number[:-1] for number in categories if len(number) > 1}
        mixed_numbers = sorted(parents_of_formulas & parents_of_categories)
        if mixed_numbers:
            number = mixed_numbers[0]
            raise FormulaTaxonomyError(
                f"Category {type(categories[number]).__name__} ({format_number(number)}) holds both "
                "subcategories and formulas; a category holds one kind only."
            )

        # --- built-in-only top levels -------------------
        # every ancestor exists after the first check, so every node's top-level category does
        for node in nodes:
            top_level = categories[node.number[:1]]
            if top_level.is_builtin_only and not is_defined_in_sunnbear(type(node)):
                raise FormulaTaxonomyError(
                    f"{type(node).__name__} ({format_number(node.number)}) is defined in {type(node).__module__}, "
                    f"but top-level category {type(top_level).__name__} ({format_number(top_level.number)}) is "
                    "reserved for nodes inside the sunnbear package."
                )
