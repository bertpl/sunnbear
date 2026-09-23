import pytest

from sunnbear.exceptions import FormulaTaxonomyError
from sunnbear.functions import FormulaCategory, FormulaRegistry

from .example_taxonomy_nodes import define_category_cls, define_formula_cls


# ==================================================================================================
#  registration
# ==================================================================================================
@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("is_formula_defined_first", [False, True])
def test_user_subcategory_under_99_registers_with_its_formulas(is_formula_defined_first):
    """Formula and category register in either order, because a category's ``__init__.py`` imports its
    formula modules before it defines the category class."""
    # --- arrange / act ----------------
    if is_formula_defined_first:
        formula = define_formula_cls((99, 1, 1))
        category = define_category_cls((99, 1))
    else:
        category = define_category_cls((99, 1))
        formula = define_formula_cls((99, 1, 1))

    # --- assert -----------------------
    assert any(type(c) is category for c in FormulaRegistry.categories())
    assert any(type(f) is formula for f in FormulaRegistry.formulas())


def test_categories_are_sorted_by_number():
    """Registered categories come out sorted by number and include every shipped top-level category and 2.1."""
    # --- act --------------------------
    numbers = [c.number for c in FormulaRegistry.categories()]

    # --- assert -----------------------
    assert numbers == sorted(numbers)
    assert {(1,), (2,), (2, 1), (3,), (99,)} <= set(numbers)


@pytest.mark.usefixtures("isolated_registry")
def test_category_declaration_from_the_docstring_registers():
    """The declaration pattern in the `FormulaCategory` docstring works as written."""

    # --- arrange / act ----------------
    class Example(FormulaCategory):
        number = (99, 50)
        name = "Example"

    # --- assert -----------------------
    assert any(type(c) is Example for c in FormulaRegistry.categories())


@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("define_first", [define_category_cls, define_formula_cls])
@pytest.mark.parametrize("define_second", [define_category_cls, define_formula_cls])
def test_duplicate_number_across_formulas_and_categories_is_rejected(define_first, define_second):
    """A number already held by a category or formula is rejected for a second category or formula."""
    # --- arrange ----------------------
    define_first((99, 1))

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"Duplicate taxonomy number 99\.1"):
        define_second((99, 1))


@pytest.mark.usefixtures("isolated_registry")
def test_builtin_only_flag_below_the_top_level_is_rejected():
    """A category below the top level that declares ``is_builtin_only`` is rejected at class definition."""
    with pytest.raises(ValueError, match="only a top-level category declares it"):
        define_category_cls((99, 1), is_builtin_only=True)


# ==================================================================================================
#  taxonomy checks, run when the registry is first queried
# ==================================================================================================
@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("define_orphan", [define_category_cls, define_formula_cls])
def test_node_without_parent_category_fails_on_read(define_orphan):
    """A category or formula whose parent category is not registered makes the next registry query fail."""
    # --- arrange ----------------------
    define_orphan((99, 7, 1))  # category (99, 7) is not defined

    # --- act / assert -----------------
    with pytest.raises(FormulaTaxonomyError, match=r"no registered parent category 99\.7"):
        FormulaRegistry.formulas()


@pytest.mark.usefixtures("isolated_registry")
def test_category_holding_subcategories_and_formulas_fails_on_read():
    """A category that holds both a subcategory and a formula makes the next registry query fail."""
    # --- arrange ----------------------
    define_category_cls((99, 1))
    define_category_cls((99, 1, 1))
    define_formula_cls((99, 1, 2))

    # --- act / assert -----------------
    with pytest.raises(FormulaTaxonomyError, match=r"\(99\.1\) holds both subcategories and formulas"):
        FormulaRegistry.categories()


@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("define_node, number", [(define_category_cls, (2, 50)), (define_formula_cls, (2, 1, 50))])
def test_node_outside_sunnbear_under_builtin_only_top_level_fails_on_read(define_node, number):
    """A node defined outside sunnbear under built-in-only category 2 makes the next registry query fail."""
    # --- arrange ----------------------
    define_node(number)  # category 2 is built-in only; this test module is outside sunnbear

    # --- act / assert -----------------
    with pytest.raises(FormulaTaxonomyError, match="reserved for nodes inside the sunnbear package"):
        FormulaRegistry.formulas()


@pytest.mark.usefixtures("isolated_registry")
def test_candidate_from_id_checks_the_taxonomy_first():
    """`candidate_from_id` raises `FormulaTaxonomyError` for an invalid tree, even for a registered formula's id."""
    # --- arrange ----------------------
    define_formula_cls((99, 7, 1))

    # --- act / assert -----------------
    with pytest.raises(FormulaTaxonomyError):
        FormulaRegistry.candidate_from_id("f2.1.1-0.2")


@pytest.mark.usefixtures("isolated_registry")
def test_registration_after_a_read_is_checked_on_the_next_read():
    """A node registered after a successful query is checked on the next query."""
    # --- arrange ----------------------
    FormulaRegistry.formulas()

    # --- act --------------------------
    define_formula_cls((99, 7, 1))

    # --- assert -----------------------
    with pytest.raises(FormulaTaxonomyError):
        FormulaRegistry.formulas()
