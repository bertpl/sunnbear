"""The table of rejected published test problems in subcategory 1.99 names existing test problems and formulas.

Each row's decision must be 1 of the file's 3 decisions, and "no action" exactly when the row has no modified test
problem; every formula of subcategory 1.99 must have a row.
"""

from pathlib import Path

from sunnbear._core.problems.catalog.c01_published_test_problems import c99_modified_published_test_problems
from sunnbear._core.problems.core import FormulaRegistry, ProblemId

_REJECTED_PUBLISHED_TEST_PROBLEMS_PATH = (
    Path(c99_modified_published_test_problems.__file__).parent / "REJECTED_PUBLISHED_TEST_PROBLEMS.md"
)


def test_published_column_holds_candidates_of_published_formulas():
    """Each row names a candidate of a formula of category 1 outside subcategory 1.99."""
    # --- arrange ----------------------
    published_ids = _candidate_ids(is_modified=False)

    # --- act --------------------------
    unknown = [
        row["Published test problem"] for row in _table_rows() if row["Published test problem"] not in published_ids
    ]

    # --- assert -----------------------
    assert unknown == []


def test_modified_column_holds_a_candidate_of_the_matching_1_99_formula():
    """A row's modified test problem is a candidate of formula 1.99.x.y.z, for its published formula 1.x.y.z."""
    # --- arrange ----------------------
    modified_ids = _candidate_ids(is_modified=True)

    # --- act --------------------------
    wrong = []
    for row in _table_rows():
        modified_id = row["Modified test problem"]
        published_formula_number = ProblemId.from_string(row["Published test problem"]).formula_number
        expected_formula_number = (1, 99, *published_formula_number[1:])
        if modified_id and (
            modified_id not in modified_ids
            or ProblemId.from_string(modified_id).formula_number != expected_formula_number
        ):
            wrong.append(modified_id)

    # --- assert -----------------------
    assert wrong == []


def test_decision_says_whether_a_row_has_a_modified_test_problem():
    """A row's decision is 1 of the doc's 3 decisions, and "no action" exactly when it has no modified test problem."""
    # --- act --------------------------
    wrong = []
    for row in _table_rows():
        has_modified_test_problem = row["Modified test problem"] != ""
        is_known_decision = row["Decision"] in {
            "all parameter tuples modified",
            "some parameter tuples modified",
            "no action",
        }
        if not is_known_decision or (row["Decision"] == "no action") == has_modified_test_problem:
            wrong.append(row["Published test problem"])

    # --- assert -----------------------
    assert wrong == []


def test_every_1_99_formula_has_a_row():
    """Each formula of subcategory 1.99 holds the modified test problem of at least 1 row."""
    # --- arrange ----------------------
    formula_numbers = {formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (1, 99)}

    # --- act --------------------------
    formula_numbers_in_table = {
        ProblemId.from_string(row["Modified test problem"]).formula_number
        for row in _table_rows()
        if row["Modified test problem"]
    }

    # --- assert -----------------------
    assert formula_numbers
    assert formula_numbers - formula_numbers_in_table == set()


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _table_rows():
    """Return the rows of the doc's table, each as a dict of column name to cell text without backticks."""
    text = _REJECTED_PUBLISHED_TEST_PROBLEMS_PATH.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.startswith("|")]
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
