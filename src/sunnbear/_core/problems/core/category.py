"""`FormulaCategory` is the base class of a formula category.

A category is an inner node of the formula taxonomy (see `taxonomy`). It holds either
subcategories or formulas, never both, and may be empty. The top-level categories are fixed: only
sunnbear defines them, and a user's categories and formulas go under the user-defined top level,
`USER_DEFINED_FORMULA_CATEGORY_NUMBER`.
"""

from typing import ClassVar

from sunnbear._core.utils.class_origin import is_sunnbear_module

from .publication import Publication
from .registry import FormulaRegistry
from .taxonomy import FormulaTaxonomyNode

# The number of the top-level category under which users register their own categories and formulas.
USER_DEFINED_FORMULA_CATEGORY_NUMBER = 99


# ==================================================================================================
#  FormulaCategory
# ==================================================================================================
class FormulaCategory(FormulaTaxonomyNode):
    """`FormulaCategory` describes one category of formulas; defining a subclass declares and registers it.

    Example::

        class SimplePolynomials(FormulaCategory):
            number = (2, 1)
            name = "Simple polynomials"

    Class attributes:
        number: The category's place in the taxonomy; its parent category is ``number[:-1]``.
        name: Display name.
        description: A text for a reader on what the category holds, in sunnbear's LaTeX notation (`presentation`),
            with its math as ``$…$`` inline and ``$$…$$`` for display. None by default; the catalog's tests require it
            of every shipped category.
        is_builtin_only: Whether this category and every node below it are reserved for classes
            defined inside the sunnbear package. Declared on top-level categories only; the
            registry applies a top-level category's flag to every node below it, and a
            subcategory's own `is_builtin_only` stays at its default `False`.
        publication: The publication of the category's formulas (`Publication`), declared by a category that holds
            exactly the formulas of 1 publication; None by default. `FormulaRegistry.publication_of` finds it for each
            formula.
        modifies_category_number: The number of the category whose formulas the formulas below this category modify,
            or None (default). A formula below this category modifies the formula with the same trailing elements
            below that category, and comes from its publication: below a category 1.99 that declares ``(1,)``,
            formula 1.99.1.6.3 modifies formula 1.1.6.3.
    """

    description: ClassVar[str | None] = None
    is_builtin_only: ClassVar[bool] = False
    publication: ClassVar[Publication | None] = None
    modifies_category_number: ClassVar[tuple[int, ...] | None] = None

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate the subclass and register it with `FormulaRegistry`.

        Raises:
            TypeError: If `number` or `name` is missing, or `number` is not a tuple of integers.
            ValueError: If `number` is empty or has an element below 1, the category is a top level
                defined outside sunnbear, `is_builtin_only` is declared below the top level, or
                registration fails (see `FormulaRegistry.register_category`).
        """
        super().__init_subclass__(**kwargs)
        cls._validate_number_and_name(min_number_length=1)
        if len(cls.number) == 1 and not is_sunnbear_module(cls.__module__):
            raise ValueError(
                f"{cls.__name__} is defined in {cls.__module__} as top-level category {cls.number[0]}; only "
                "sunnbear defines top-level categories, so put user categories and formulas under "
                f"{USER_DEFINED_FORMULA_CATEGORY_NUMBER}."
            )
        if "is_builtin_only" in cls.__dict__ and len(cls.number) > 1:
            raise ValueError(
                f"{cls.__name__} declares is_builtin_only below the top level; only a top-level category "
                "declares it, and every node below inherits it."
            )
        FormulaRegistry.register_category(cls)
