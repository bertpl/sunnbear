"""Each shipped formula and category declares what a reader sees of it, and each formula applies ``c`` as it declares.

The checks of a formula's own notation, placeholders and definitions run when its class is defined (`Formula`,
`FormulaPresentation`); these tests add the requirements that apply only to the shipped formulas and categories.

The tests of how category 1's formulas apply ``c`` live with the survey of published test problems, in
`tests/scripts/`, because they use the rule of category 1 for the size of the shift.
"""

import pytest

import sunnbear._core.problems.catalog as catalog
from sunnbear._core.problems.core import Formula, FormulaCategory, FormulaRegistry
from tests.problems.effect_of_c_check import follows_effect_of_c

_CATALOG_PREFIX = f"{catalog.__name__}."
_SHIPPED_FORMULAS = [
    formula for formula in FormulaRegistry.formulas() if type(formula).__module__.startswith(_CATALOG_PREFIX)
]
_SHIPPED_CATEGORIES = [
    category for category in FormulaRegistry.categories() if type(category).__module__.startswith(_CATALOG_PREFIX)
]
_FORMULAS_TO_CHECK_FOR_C = [
    formula for formula in _SHIPPED_FORMULAS if formula.effect_of_c is not None and formula.number[0] != 1
]
_INCOMPLETE = "the presentations of the catalog's formulas and categories are not complete"


def _texts_for_a_reader(formula: Formula) -> list[str]:
    """Return the formula's texts for a reader: summary, notes, its parameters' meanings and its recipes' summaries."""
    texts = [param.meaning for param in formula.params if param.meaning is not None]
    texts += [recipe.summary for recipe in formula.recipes() if recipe.summary is not None]
    if formula.presentation is not None:
        texts += formula.presentation.texts_for_a_reader
    return texts


# ==================================================================================================
#  Texts for a reader
# ==================================================================================================
@pytest.mark.parametrize("formula", _SHIPPED_FORMULAS, ids=lambda formula: formula.label)
def test_formula_texts_hold_no_code(formula):
    """A text for a reader names no class or constant of sunnbear's code, so it holds no code span in backticks."""
    assert [text for text in _texts_for_a_reader(formula) if "`" in text] == []


@pytest.mark.parametrize("category", _SHIPPED_CATEGORIES, ids=lambda category: category.label)
def test_category_description_holds_no_code(category):
    """A category's description names no class or constant of sunnbear's code, so it holds no code span."""
    assert category.description is None or "`" not in category.description


@pytest.mark.parametrize("formula", _SHIPPED_FORMULAS, ids=lambda formula: formula.label)
def test_recipe_summaries_name_only_parameters(formula):
    """A recipe's summary names only parameters of its formula, and renders with their symbols."""
    # --- arrange ----------------------
    summaries = [recipe.summary for recipe in formula.recipes() if recipe.summary is not None]

    # --- act / assert -----------------
    for summary in summaries:
        formula.latex_with_symbols(summary)


# ==================================================================================================
#  Required declarations
# ==================================================================================================
@pytest.mark.skip(reason=_INCOMPLETE)
@pytest.mark.parametrize("formula", _SHIPPED_FORMULAS, ids=lambda formula: formula.label)
def test_formula_declares_what_a_reader_sees(formula):
    """A shipped formula declares its presentation, how it applies ``c``, its symbols and its recipes' summaries."""
    assert formula.presentation is not None
    assert formula.effect_of_c is not None
    assert [param.name for param in formula.params if param.latex_symbol is None] == []
    assert [recipe for recipe in formula.recipes() if recipe.summary is None] == []


@pytest.mark.skip(reason=_INCOMPLETE)
@pytest.mark.parametrize("formula", _SHIPPED_FORMULAS, ids=lambda formula: formula.label)
def test_formula_declares_its_summary(formula):
    """A shipped formula's presentation holds its summary."""
    assert formula.presentation is not None
    assert formula.presentation.summary is not None


@pytest.mark.skip(reason=_INCOMPLETE)
@pytest.mark.parametrize("category", _SHIPPED_CATEGORIES, ids=lambda category: category.label)
def test_category_declares_its_description(category: FormulaCategory):
    """A shipped category declares its description for a reader."""
    assert category.description is not None


# ==================================================================================================
#  How c applies
# ==================================================================================================
@pytest.mark.parametrize("formula", _FORMULAS_TO_CHECK_FOR_C, ids=lambda formula: formula.label)
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
