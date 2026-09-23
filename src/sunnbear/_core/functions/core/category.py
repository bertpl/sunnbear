"""`FormulaCategory` is the base class of a formula category.

A category is an inner node of the formula taxonomy (see `taxonomy`). It holds either
subcategories or formulas, never both, and may be empty. The top-level categories are fixed: only
sunnbear defines them, and a user's categories and formulas go under the user-defined top level.
"""

from typing import ClassVar

from sunnbear._core.utils.class_origin import is_defined_in_sunnbear

from .registry import FormulaRegistry
from .taxonomy import FormulaTaxonomyNode


# ==================================================================================================
#  FormulaCategory
# ==================================================================================================
class FormulaCategory(FormulaTaxonomyNode):
    """`FormulaCategory` describes one category of formulas; defining a subclass declares and registers it.

    Example::

        class Polynomials(FormulaCategory):
            number = (2, 1)
            name = "Polynomials"

    Class attributes:
        number: The category's place in the taxonomy; its parent category is ``number[:-1]``.
        name: Display name.
        is_builtin_only: Whether this category and every node below it are reserved for classes
            defined inside the sunnbear package. Declared on top-level categories only; the
            registry applies a top-level category's flag to every node below it, and a
            subcategory's own `is_builtin_only` stays at its default `False`.
    """

    is_builtin_only: ClassVar[bool] = False

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
        if len(cls.number) == 1 and not is_defined_in_sunnbear(cls):
            raise ValueError(
                f"{cls.__name__} is defined in {cls.__module__} as top-level category {cls.number[0]}; only "
                "sunnbear defines top-level categories, so put user categories and formulas under 99."
            )
        if "is_builtin_only" in cls.__dict__ and len(cls.number) > 1:
            raise ValueError(
                f"{cls.__name__} declares is_builtin_only below the top level; only a top-level category "
                "declares it, and every node below inherits it."
            )
        FormulaRegistry.register_category(cls)
