"""The formula registry holds formulas and categories, and rebuilds a candidate test function from an identity.

Defining a concrete `Formula` or a `FormulaCategory` subclass registers one instance of it here,
as a node of the formula taxonomy (see `taxonomy`). Checks run in 2 stages:

- **At class definition**, the checks that concern the formula or category alone, so a malformed
  one fails when its module is imported:

  - a valid number and name
  - no other registered node with the same number
  - for a category: a top level only when defined inside sunnbear, and `is_builtin_only`
    declared only at the top level

- **The first time the registry is queried**, and again on the first query after any later
  registration, the checks across nodes:

  - every node's parent category exists
  - no category holds both subcategories and formulas
  - no node outside sunnbear sits under a built-in-only top-level category (see
    `FormulaCategory.is_builtin_only`)

  The checks across nodes cannot run at class definition: a category's package imports its
  formula modules at the top of its ``__init__.py``, so its formulas register before the
  category itself.

The registry itself imports nothing: the shipped formulas and categories are registered when the
test-function package imports the formula catalog.
"""

from typing import TYPE_CHECKING, ClassVar

from sunnbear._core.utils.class_origin import is_defined_in_sunnbear

from .exceptions import FormulaTaxonomyError, InvalidParamsError, UnknownFormulaError
from .identity import FunctionId
from .taxonomy import FormulaTaxonomyNode
from .test_function import CandidateTestFunction

# type-only: formula and category import this module at runtime, so a runtime import would be circular
if TYPE_CHECKING:
    from .category import FormulaCategory
    from .formula import Formula


# ==================================================================================================
#  FormulaRegistry
# ==================================================================================================
class FormulaRegistry:
    """`FormulaRegistry` enumerates formulas and categories, or rebuilds a candidate test function from an identity.

    `Formula.__init_subclass__` and `FormulaCategory.__init_subclass__` call `register_formula` and
    `register_category`, so the registry is complete as soon as the modules that define the formula and
    category subclasses are imported.
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
        cls._validate_number_is_free(formula)
        cls._formulas_by_number[formula.number] = formula
        cls._is_taxonomy_validated = False

    @classmethod
    def register_category(cls, category_cls: "type[FormulaCategory]") -> None:
        """Instantiate a category class and register it under its number.

        Raises:
            ValueError: If another registered formula or category has the same number.
        """
        category = category_cls()
        cls._validate_number_is_free(category)
        cls._categories_by_number[category.number] = category
        cls._is_taxonomy_validated = False

    # --------------------------------------------------------------------------
    #  Queries
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
            InvalidParamsError: If the parameter names differ from the formula's `param_names`, or the
                parameter tuple fails the formula's validity criteria.
        """
        cls._ensure_taxonomy_validated()
        fid = FunctionId.from_string(function_id) if isinstance(function_id, str) else function_id
        formula = cls._formulas_by_number.get(fid.formula_number)
        if formula is None:
            raise UnknownFormulaError(
                f"No registered formula with number {FormulaTaxonomyNode.format_number(fid.formula_number)} "
                f"(id: {fid})."
            )
        if fid.param_names != formula.param_names:
            raise InvalidParamsError(
                f"Parameter names {list(fid.param_names)} do not match the parameters {list(formula.param_names)} "
                f"of formula {formula.name} (id: {fid})."
            )
        if not formula.is_param_tuple_valid(*fid.param_values):
            raise InvalidParamsError(f"Parameter values are invalid for formula {formula.name} (id: {fid}).")
        return formula.build_candidate(fid.param_values)

    # --------------------------------------------------------------------------
    #  Taxonomy checks
    # --------------------------------------------------------------------------
    @classmethod
    def _validate_number_is_free(cls, node: FormulaTaxonomyNode) -> None:
        """Check that no registered formula or category has the number of `node`.

        Raises:
            ValueError: If a registered formula or category already has that number.
        """
        existing_node = cls._formulas_by_number.get(node.number) or cls._categories_by_number.get(node.number)
        if existing_node is not None:
            raise ValueError(
                f"Duplicate taxonomy number {FormulaTaxonomyNode.format_number(node.number)}: "
                f"{type(node).__name__} and {type(existing_node).__name__}."
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
        nodes: list[FormulaTaxonomyNode] = [*categories.values(), *cls._formulas_by_number.values()]

        # --- every parent exists ----------------
        # a formula's number has at least 2 elements, so only a top-level category has no parent
        for node in nodes:
            parent_number = node.number[:-1]
            if parent_number and parent_number not in categories:
                raise FormulaTaxonomyError(
                    f"{node.label} has no registered parent category "
                    f"{FormulaTaxonomyNode.format_number(parent_number)}."
                )

        # --- no mixed categories ----------------
        formula_parent_numbers = {number[:-1] for number in cls._formulas_by_number}
        category_parent_numbers = {number[:-1] for number in categories if len(number) > 1}
        mixed_category_numbers = sorted(formula_parent_numbers & category_parent_numbers)
        if mixed_category_numbers:
            raise FormulaTaxonomyError(
                f"Category {categories[mixed_category_numbers[0]].label} holds both subcategories and formulas; "
                "a category holds one kind only."
            )

        # --- built-in-only top levels -----------
        # the parent check above guarantees that every ancestor exists, including each node's top-level category
        for node in nodes:
            top_level_category = categories[node.number[:1]]
            if top_level_category.is_builtin_only and not is_defined_in_sunnbear(type(node)):
                raise FormulaTaxonomyError(
                    f"{node.label} is defined in {type(node).__module__}, but top-level category "
                    f"{top_level_category.label} is reserved for nodes inside the sunnbear package."
                )
