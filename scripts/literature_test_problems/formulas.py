"""This module builds `formulas.csv`, which maps each formula id of category 1 to the `new` rows that the formula holds.

The folder's README gives the rules: which sources get a number, the order of the sources and of their formulas, and
when several rows share a formula.
"""

import csv
import io
from collections import Counter
from dataclasses import dataclass

from .data_files import FormulaDecision, RowsTableLine, join_row_ids

FORMULAS_COLUMNS = ["formula_id", "source_id", "row_ids", "variable_change"]


# ==================================================================================================
#  FormulaMapping
# ==================================================================================================
@dataclass(frozen=True)
class FormulaMapping:
    """A `FormulaMapping` holds the formulas of category 1 in id order, each with the `new` rows that it holds."""

    formulas: tuple["FormulasTableLine", ...]

    def csv_text(self) -> str:
        """Return the text of `formulas.csv`, with Unix line endings."""
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=FORMULAS_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(formula.to_csv_line() for formula in self.formulas)
        return text.getvalue()

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def build(cls, rows: list[RowsTableLine], formula_decisions: list[FormulaDecision]) -> "FormulaMapping":
        """Return the formulas of the `new` rows, for rows given in time order.

        Within each subcategory, the sources that have a `new` row are numbered in time order. Within a source, the
        formulas follow the order of its rows, and a formula of several rows takes the place of its first row. A
        `new` row that no decision names is a formula of its own.
        """
        decision_by_row_id = {row_id: decision for decision in formula_decisions for row_id in decision.row_ids}
        new_rows_by_source: dict[str, list[RowsTableLine]] = {}
        for row in rows:
            if row.final_status.status == "new":
                new_rows_by_source.setdefault(row.source_id, []).append(row)
        n_sources_by_subcategory: Counter[str] = Counter()
        formulas = []
        for source_id, new_rows in new_rows_by_source.items():
            subcategory = new_rows[0].subcategory
            n_sources_by_subcategory[subcategory] += 1
            source_number = (*(int(part) for part in subcategory.split(".")), n_sources_by_subcategory[subcategory])
            placed_row_ids: set[str] = set()
            formula_number = 0
            for row in new_rows:
                if row.row_id in placed_row_ids:
                    continue
                decision = decision_by_row_id.get(row.row_id)
                if decision is None:
                    row_ids, variable_change = (row.row_id,), ""
                else:
                    # the decision's rows in the order of the source; FormulaDecision.find_problems reports the others
                    row_ids = tuple(r.row_id for r in new_rows if r.row_id in decision.row_ids)
                    variable_change = decision.variable_change
                placed_row_ids.update(row_ids)
                formula_number += 1
                formulas.append(
                    FormulasTableLine((*source_number, formula_number), source_id, row_ids, variable_change)
                )
        return cls(tuple(sorted(formulas, key=lambda formula: formula.number)))


# ==================================================================================================
#  FormulasTableLine
# ==================================================================================================
@dataclass(frozen=True)
class FormulasTableLine:
    """A `FormulasTableLine` holds 1 line of `formulas.csv`: a formula's number, its source and its `new` rows.

    `number` is the formula's place in the catalog's tree: category 1, the subcategory, the source and the formula,
    such as `(1, 4, 12, 3)`. `variable_change` is empty unless the formula takes another variable than its row's f.
    """

    number: tuple[int, ...]
    source_id: str
    row_ids: tuple[str, ...]
    variable_change: str

    @property
    def formula_id(self) -> str:
        """Return the formula's id, its number with dots and an `f` prefix, such as `f1.4.12.3`."""
        return "f" + ".".join(str(part) for part in self.number)

    def to_csv_line(self) -> dict[str, str]:
        """Return the formula as 1 line of `formulas.csv`, keyed by column."""
        return {
            "formula_id": self.formula_id,
            "source_id": self.source_id,
            "row_ids": join_row_ids(self.row_ids),
            "variable_change": self.variable_change,
        }
