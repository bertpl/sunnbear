import pytest

from sunnbear._core.functions.core.taxonomy import FormulaTaxonomyNode
from sunnbear.functions import FormulaCategory

from .example_taxonomy_nodes import define_category_cls, define_formula_cls


# ==================================================================================================
#  FormulaTaxonomyNode.format_number / parse_number
# ==================================================================================================
@pytest.mark.parametrize("number, text", [((2,), "2"), ((2, 1, 1), "2.1.1"), ((99, 10, 123), "99.10.123")])
def test_number_renders_and_parses_back(number, text):
    """A taxonomy number renders with dots and parses back to the same tuple."""
    # --- act / assert -----------------
    assert FormulaTaxonomyNode.format_number(number) == text
    assert FormulaTaxonomyNode.parse_number(text) == number


@pytest.mark.parametrize("text", ["", "2.", ".2", "2..1", "0", "2.01", "2.-1", "2.a", "2,1"])
def test_parse_number_rejects_invalid(text):
    """Parsing rejects text that is not a dot-separated list of positive integers without leading zeros."""
    with pytest.raises(ValueError, match="Invalid taxonomy number"):
        FormulaTaxonomyNode.parse_number(text)


# ==================================================================================================
#  number validation
# ==================================================================================================
@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize(
    "number, error, match",
    [
        ((), ValueError, "at least 1 element"),
        ((99, 0), ValueError, "only positive integers"),
        ([99, 1], TypeError, "tuple of integers"),
        ((99, True), TypeError, "tuple of integers"),
        ((99, 1.0), TypeError, "tuple of integers"),
    ],
)
def test_category_number_is_validated_at_class_definition(number, error, match):
    """A category number that is empty, non-positive, not a tuple, or holds a non-int is rejected when defined."""
    with pytest.raises(error, match=match):
        define_category_cls(number)


@pytest.mark.usefixtures("isolated_registry")
def test_formula_number_needs_a_parent_category_element():
    """A formula is a leaf under a category, so its number has at least 2 elements."""
    with pytest.raises(ValueError, match="at least 2 element"):
        define_formula_cls((99,))


@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("attrs, missing", [({"name": "No number"}, "number"), ({"number": (99, 1)}, "name")])
def test_number_and_name_are_required(attrs, missing):
    """A category class without ``number`` or ``name`` is rejected at class definition."""
    with pytest.raises(TypeError, match=f"must define {missing}"):
        type("Incomplete", (FormulaCategory,), attrs)
