"""This category holds the modified versions of the formulas of Foo, Tan (2025)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_section_4_2, f02_section_4_3_1


class ModifiedFooTan2025(FormulaCategory):
    """`ModifiedFooTan2025` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.2.15, `FooTan2025`, and come from the publication of `FooTan2025`.
    """

    number = (1, 99, 2, 15)
    name = "Foo, Tan (2025)"
    description = (
        "The test problems are modified versions of those that come from a preprint that introduces a "
        "higher-order root-finding method and applies it to entropy functions."
    )
