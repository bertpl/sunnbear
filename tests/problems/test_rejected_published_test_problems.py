"""The table of rejected published test problems in subcategory 1.99 names existing test problems and formulas."""

from pathlib import Path

import sunnbear._core.problems.catalog.c01_published_test_problems.c99_modified_published_test_problems as subcategory
from sunnbear._core.problems.core import FormulaRegistry

_DOC = Path(subcategory.__file__).parent / "REJECTED_PUBLISHED_TEST_PROBLEMS.md"
_DECISIONS = {"formula modified", "tuples modified", "no action"}


def test_published_column_names_candidates_of_published_formulas():
    """Each row names a candidate of a formula of category 1 outside subcategory 1.99."""
    # --- arrange ----------------------
    published_ids = _candidate_ids(is_modified=False)

    # --- act --------------------------
    unknown = [
        row["Published test problem"] for row in _table_rows() if row["Published test problem"] not in published_ids
    ]

    # --- assert -----------------------
    assert unknown == []


def test_modified_column_names_a_candidate_of_the_matching_1_99_formula():
    """A row's modified test problem is a candidate of formula 1.99.x.y.z, for its published formula 1.x.y.z."""
    # --- arrange ----------------------
    modified_ids = _candidate_ids(is_modified=True)

    # --- act --------------------------
    wrong = []
    for row in _table_rows():
        modified_id = row["Modified test problem"]
        expected_formula_id = "f1.99." + row["Published test problem"].split("[")[0].removeprefix("f1.")
        if modified_id and (modified_id not in modified_ids or modified_id.split("[")[0] != expected_formula_id):
            wrong.append(modified_id)

    # --- assert -----------------------
    assert wrong == []


def test_decision_says_whether_a_row_has_a_modified_test_problem():
    """A row's decision is 1 of the 3, and "no action" exactly when the row has no modified test problem."""
    # --- act --------------------------
    wrong = [
        row["Published test problem"]
        for row in _table_rows()
        if row["Decision"] not in _DECISIONS or (row["Decision"] == "no action") != (row["Modified test problem"] == "")
    ]

    # --- assert -----------------------
    assert wrong == []


def test_every_1_99_formula_has_a_row():
    """Each formula of subcategory 1.99 holds the modified test problem of at least 1 row."""
    # --- arrange ----------------------
    formula_ids = {
        f"f{formula.format_number(formula.number)}"
        for formula in FormulaRegistry.formulas()
        if formula.number[:2] == (1, 99)
    }

    # --- act --------------------------
    formula_ids_in_table = {row["Modified test problem"].split("[")[0] for row in _table_rows()}

    # --- assert -----------------------
    assert formula_ids
    assert formula_ids - formula_ids_in_table == set()


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _table_rows():
    """Return the rows of the doc's table, each as a dict of column name to cell text without backticks."""
    lines = [line for line in _DOC.read_text(encoding="utf-8").splitlines() if line.startswith("|")]
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    # lines[1] is the separator line of the table
    return [
        dict(zip(header, [cell.strip().strip("`") for cell in line.strip("|").split("|")], strict=True))
        for line in lines[2:]
    ]


def _candidate_ids(*, is_modified):
    """Return the ids of the candidates of the formulas of category 1 inside or outside subcategory 1.99."""
    return {
        str(candidate.id)
        for formula in FormulaRegistry.formulas()
        if formula.number[0] == 1 and (formula.number[1] == 99) == is_modified
        for candidate in formula.build_all_candidates()
    }
