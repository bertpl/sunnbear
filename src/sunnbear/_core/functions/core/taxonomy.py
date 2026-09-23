"""The formula taxonomy is a tree whose inner nodes are categories and whose leaves are formulas.

Every node has a number: a tuple of positive integers, e.g. ``(2, 1, 1)``, rendered ``2.1.1``.
Dropping the last element of a node's number gives its parent's number, so ``(2, 1)`` is the
parent of ``(2, 1, 1)``.

The number of a formula therefore names the formula's categories from the top level down, and
sorting by number sorts in category order.

`TaxonomyNode` is the base class of `Formula` and `FormulaCategory` and holds what the 2 kinds
of node share.

`FormulaRegistry` checks how the nodes relate to one another; its module docstring says when.
"""

import re
import unicodedata
from typing import ClassVar


# ==================================================================================================
#  TaxonomyNode
# ==================================================================================================
class TaxonomyNode:
    """`TaxonomyNode` is the base class of a node of the formula taxonomy: a category or a formula.

    Class attributes:
        number: The node's place in the taxonomy, a non-empty tuple of positive integers.
        name: Display name, e.g. "Odd power".
    """

    number: ClassVar[tuple[int, ...]]
    name: ClassVar[str]

    @property
    def name_slug(self) -> str:
        """Return `name` as a lowercase identifier, e.g. ``odd_power``; catalog file names carry it."""
        return slugify(self.name)

    @property
    def label(self) -> str:
        """Return the class name and dotted number, e.g. ``Cubic (2.1.1)``, for error messages."""
        return f"{type(self).__name__} ({format_taxonomy_number(self.number)})"

    @classmethod
    def _validate_number_and_name(cls, min_number_length: int) -> None:
        """Check that `number` and `name` are declared; `number` needs `min_number_length` or more positive integers.

        Raises:
            TypeError: If `number` or `name` is missing, or `number` is not a tuple of integers.
            ValueError: If `number` is shorter than `min_number_length`, or has an element below 1.
        """
        for attr in ("number", "name"):
            if not hasattr(cls, attr):
                raise TypeError(f"{cls.__name__} must define {attr}.")
        number = cls.number
        # bool is an int subclass, but True as a number element is certainly a mistake
        if not isinstance(number, tuple) or any(isinstance(n, bool) or not isinstance(n, int) for n in number):
            raise TypeError(f"{cls.__name__}.number must be a tuple of integers (got {number!r}).")
        if len(number) < min_number_length:
            raise ValueError(
                f"{cls.__name__}.number must have at least {min_number_length} element(s) (got {number!r})."
            )
        if any(n < 1 for n in number):
            raise ValueError(f"{cls.__name__}.number must contain only positive integers (got {number!r}).")


# ==================================================================================================
#  Helpers
# ==================================================================================================
def format_taxonomy_number(number: tuple[int, ...]) -> str:
    """Render a taxonomy number with dots, e.g. ``(2, 1, 1)`` as ``2.1.1``."""
    return ".".join(str(n) for n in number)


def parse_taxonomy_number(text: str) -> tuple[int, ...]:
    """Parse a rendered taxonomy number, e.g. ``2.1.1``, back into a tuple.

    Raises:
        ValueError: If `text` is not a dot-separated list of positive integers.
    """
    if not re.fullmatch(r"[1-9][0-9]*(\.[1-9][0-9]*)*", text):
        raise ValueError(f"Invalid taxonomy number: {text!r}")
    return tuple(int(part) for part in text.split("."))


def slugify(name: str) -> str:
    """Return `name` as a lowercase identifier, e.g. "Standard function families" as ``standard_function_families``.

    The conversion runs in 3 steps:

    - accented letters lose their accent, and other non-ASCII characters are dropped
    - each run of characters outside a-z and 0-9 becomes 1 underscore
    - leading and trailing underscores are removed

    The result is a valid Python module name as long as it does not start with a digit.
    """
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")
