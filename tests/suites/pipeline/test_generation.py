"""`generate_candidates` lists every candidate of every formula, formula by formula, with its id and interval bounds."""

import polars as pl
import pytest

from sunnbear._core.functions.core import FormulaRegistry
from sunnbear._core.suites.pipeline.generation import CANDIDATES_SCHEMA, generate_candidates


@pytest.mark.parametrize(
    "formula_numbers",
    [
        pytest.param(((2, 1, 2), (2, 1, 1)), id="2_formulas_against_number_order"),
        pytest.param((), id="no_formulas"),
    ],
)
def test_the_candidates_are_listed_formula_by_formula_in_the_given_order(formula_numbers):
    """The rows are each formula's candidates in the order of `Formula.build_all_candidates`, formula by formula in
    the given order, typed by `CANDIDATES_SCHEMA`."""
    # --- arrange ----------------------
    formulas_by_number = {formula.number: formula for formula in FormulaRegistry.formulas()}
    formulas = [formulas_by_number[number] for number in formula_numbers]
    rows_expected = [
        (str(candidate.id), candidate.a, candidate.b)
        for formula in formulas
        for candidate in formula.build_all_candidates()
    ]

    # --- act --------------------------
    candidates = generate_candidates(formulas)

    # --- assert -----------------------
    assert candidates.schema == pl.Schema(CANDIDATES_SCHEMA)
    assert candidates.rows() == rows_expected
