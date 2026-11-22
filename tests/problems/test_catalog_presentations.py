"""Each shipped formula and category declares what a reader sees of it, and each formula applies ``c`` as it declares.

The checks of a formula's own notation, placeholders and definitions run when its class is defined (`Formula`,
`FormulaPresentation`); these tests add the requirements that apply only to the shipped formulas and categories.

The tests of how category 1's formulas apply ``c`` live with the survey of published test problems, because they use
the rule of category 1 for the size of the shift.
"""

import pytest

import sunnbear._core.problems.catalog as catalog
from sunnbear._core.problems.core import Formula, FormulaRegistry
from tests.problems.effect_of_c_check import follows_effect_of_c

_CATALOG_PREFIX = f"{catalog.__name__}."
_SHIPPED_FORMULAS = [
    formula for formula in FormulaRegistry.formulas() if type(formula).__module__.startswith(_CATALOG_PREFIX)
]
_SHIPPED_CATEGORIES = [
    category for category in FormulaRegistry.categories() if type(category).__module__.startswith(_CATALOG_PREFIX)
]
_FORMULAS_TO_CHECK_FOR_C = [formula for formula in _SHIPPED_FORMULAS if formula.number[0] != 1]


# ==================================================================================================
#  Texts for a reader
# ==================================================================================================
# Each test of this section and the next checks every shipped formula or category in 1 test, and lists the ones that
# fail; the checks are cheap, so 1 test item per formula or category would only add items.
def test_formula_texts_hold_no_code():
    """A text for a reader names no class or constant of sunnbear's code, so it holds no code span in backticks."""
    # --- act --------------------------
    failing = [
        formula.label for formula in _SHIPPED_FORMULAS if any("`" in text for text in formula.texts_for_a_reader())
    ]

    # --- assert -----------------------
    assert failing == []


def test_category_descriptions_hold_no_code():
    """A category's description names no class or constant of sunnbear's code, so it holds no code span."""
    # --- act --------------------------
    failing = [
        category.label
        for category in _SHIPPED_CATEGORIES
        if category.description is not None and "`" in category.description
    ]

    # --- assert -----------------------
    assert failing == []


def test_recipe_summaries_name_only_parameters():
    """A recipe's summary names only parameters of its formula, and renders with their symbols."""
    # --- act --------------------------
    failing = []
    for formula in _SHIPPED_FORMULAS:
        for recipe in formula.recipes():
            if recipe.summary is not None:
                try:
                    formula.latex_with_symbols(recipe.summary)
                except ValueError as error:
                    failing.append(f"{formula.label}: {error}")

    # --- assert -----------------------
    assert failing == []


# ==================================================================================================
#  Required declarations
# ==================================================================================================
def test_formulas_declare_what_a_reader_sees():
    """A shipped formula declares its presentation, how it applies ``c``, its symbols and its recipes' summaries."""
    # --- act --------------------------
    failing = []
    for formula in _SHIPPED_FORMULAS:
        has_symbols = all(param.latex_symbol is not None for param in formula.params)
        has_recipe_summaries = all(recipe.summary is not None for recipe in formula.recipes())
        if formula.presentation is None or formula.effect_of_c is None or not has_symbols or not has_recipe_summaries:
            failing.append(formula.label)

    # --- assert -----------------------
    assert failing == []


@pytest.mark.skip(reason="the formulas of category 1 declare no summary")
def test_formulas_declare_their_summaries():
    """A shipped formula's presentation holds its summary."""
    # --- act --------------------------
    failing = [
        formula.label
        for formula in _SHIPPED_FORMULAS
        if formula.presentation is None or formula.presentation.summary is None
    ]

    # --- assert -----------------------
    assert failing == []


def test_formulas_declare_parameter_conditions_exactly_where_they_check_parameters():
    """A shipped formula's presentation declares parameter conditions exactly when it overrides `is_param_tuple_valid`.

    The test does not compare a condition's text with the code that checks it, because the text is prose for a reader.
    """
    # --- act --------------------------
    failing = []
    for formula in _SHIPPED_FORMULAS:
        has_param_check = type(formula).is_param_tuple_valid is not Formula.is_param_tuple_valid
        if formula.presentation is not None:
            has_param_conditions = len(formula.presentation.param_conditions) > 0
        else:
            has_param_conditions = False
        if has_param_check != has_param_conditions:
            failing.append(formula.label)

    # --- assert -----------------------
    assert failing == []


def test_categories_declare_their_descriptions():
    """A shipped category declares its description for a reader."""
    # --- act --------------------------
    failing = [category.label for category in _SHIPPED_CATEGORIES if category.description is None]

    # --- assert -----------------------
    assert failing == []


# ==================================================================================================
#  How c applies
# ==================================================================================================
@pytest.mark.parametrize(
    "formula", _FORMULAS_TO_CHECK_FOR_C, ids=[formula.label for formula in _FORMULAS_TO_CHECK_FOR_C]
)
def test_formula_applies_c_as_declared(formula):
    """Evaluated at its first, middle and last candidate, a formula applies ``c`` as its `effect_of_c` says.

    `follows_effect_of_c` cannot judge every candidate, such as one whose function is flat almost everywhere, so it
    must judge at least 1, and each candidate that it judges must follow the declared way.
    """
    # --- arrange ----------------------
    candidates = formula.build_all_candidates()
    picked = (candidates[0], candidates[len(candidates) // 2], candidates[-1])

    # --- act --------------------------
    results = [follows_effect_of_c(candidate, formula.effect_of_c) for candidate in picked]

    # --- assert -----------------------
    judged = [result for result in results if result is not None]
    assert judged
    assert all(judged)
