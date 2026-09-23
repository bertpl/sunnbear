"""`FormulaCategory` is the base class of a formula category.

A category is an inner node of the formula taxonomy (see `taxonomy`). It holds either
subcategories or formulas, never both, and may be empty.
"""

from typing import ClassVar

from .registry import FormulaRegistry
from .taxonomy import TaxonomyNode


# ==================================================================================================
#  FormulaCategory
# ==================================================================================================
class FormulaCategory(TaxonomyNode):
    """`FormulaCategory` describes one category of formulas; defining a subclass declares and registers it.

    Example::

        class Polynomials(FormulaCategory):
            number = (2, 1)
            name = "Polynomials"

    Class attributes:
        number: The category's place in the taxonomy; its parent category is ``number[:-1]``.
        name: Display name.
        is_builtin_only: Whether this category and every node below it are reserved for classes
            defined inside the sunnbear package. Declared on top-level categories only; every
            node below a top-level category inherits that category's flag.
    """

    is_builtin_only: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate the subclass and register it with `FormulaRegistry`.

        Raises:
            TypeError: If `number` or `name` is missing, or `number` is not a tuple of integers.
            ValueError: If `number` is empty or has an element below 1, `is_builtin_only` is declared
                below the top level, or registration fails (see `FormulaRegistry.register_category`).
        """
        super().__init_subclass__(**kwargs)
        cls._validate_number_and_name(min_length=1)
        if "is_builtin_only" in cls.__dict__ and len(cls.number) > 1:
            raise ValueError(
                f"{cls.__name__} declares is_builtin_only below the top level; only a top-level category "
                "declares it, and every node below inherits it."
            )
        FormulaRegistry.register_category(cls)
