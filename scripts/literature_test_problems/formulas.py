"""This module builds `formulas.csv`, which maps each formula id of category 1 to its rows, and reads it back.

The folder's README gives the rules: which sources get a number, how the ids of new formulas are appended to the ids
already given, and when several rows share a formula.
"""

import csv
import io
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path

from .data_files import DataFileError, FormulaDecision, RowsTableLine, join_row_ids, split_row_ids

FORMULA_COLUMNS = ["formula_id", "status", "source_id", "row_ids", "variable_change"]
FORMULA_STATUSES = ("active", "retired")


class FormulaIdChangeError(ValueError):
    """A `FormulaIdChangeError` reports changes that would change the id of a formula, which a person must resolve."""

    def __init__(self, problems: list[str]) -> None:
        """Keep `problems`, 1 sentence per change, and join them into the message."""
        super().__init__("; ".join(problems))
        self.problems = problems


# ==================================================================================================
#  FormulasTable
# ==================================================================================================
@dataclass(frozen=True)
class FormulasTable:
    """A `FormulasTable` holds the formulas of category 1 in id order, active and retired, each with its rows."""

    formulas: tuple["FormulasTableLine", ...]

    def csv_text(self) -> str:
        """Return the text of `formulas.csv`, with Unix line endings."""
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=FORMULA_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(formula.to_csv_line() for formula in self.formulas)
        return text.getvalue()

    def find_problems(self, rows: list[RowsTableLine]) -> list[str]:
        """Return the problems of the table's formulas against `rows`, the rows of `rows.csv`.

        A formula has a problem if it names a row that no longer exists, or if its source is now in another
        subcategory than the formula's number says.
        """
        problems = []
        known_row_ids = {row.row_id for row in rows}
        subcategory_number_by_source = {row.source_id: row.subcategory_number for row in rows}
        for formula in self.formulas:
            unknown_row_ids = [row_id for row_id in formula.row_ids if row_id not in known_row_ids]
            if unknown_row_ids:
                problems.append(f"{formula.formula_id} names a row that no longer exists, {unknown_row_ids[0]}")
            elif formula.number[:2] != subcategory_number_by_source[formula.source_id]:
                problems.append(f"the source of {formula.formula_id} is now in another subcategory")
        return problems

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _group_new_rows(
        rows: list[RowsTableLine], formula_decisions: list[FormulaDecision]
    ) -> dict[str, list[tuple[tuple[str, ...], str]]]:
        """Return the formulas of each source's `new` rows, with each formula's rows and variable change.

        The sources come in time order and their formulas in the order of their rows: a formula of several rows comes
        at the position of its first row. A `new` row that no decision names is a formula of its own.
        """
        formula_decision_by_row_id = {
            row_id: formula_decision for formula_decision in formula_decisions for row_id in formula_decision.row_ids
        }
        new_rows_by_source: dict[str, list[RowsTableLine]] = {}
        for row in rows:
            if row.final_status.status == "new":
                new_rows_by_source.setdefault(row.source_id, []).append(row)
        formulas_by_source: dict[str, list[tuple[tuple[str, ...], str]]] = {}
        for source_id, new_rows in new_rows_by_source.items():
            placed_row_ids: set[str] = set()
            for row in new_rows:
                if row.row_id in placed_row_ids:
                    continue
                formula_decision = formula_decision_by_row_id.get(row.row_id)
                if formula_decision is None:
                    row_ids, variable_change = (row.row_id,), ""
                else:
                    # keep the decision's rows that are `new` rows of this source, in the source's order;
                    # FormulaDecision.find_problems reports the other rows that the decision names
                    row_ids = tuple(r.row_id for r in new_rows if r.row_id in formula_decision.row_ids)
                    variable_change = formula_decision.variable_change
                placed_row_ids.update(row_ids)
                formulas_by_source.setdefault(source_id, []).append((row_ids, variable_change))
        return formulas_by_source

    @staticmethod
    def _next_free_number(prefix: tuple[int, ...], formulas: Iterable["FormulasTableLine"]) -> tuple[int, ...]:
        """Return `prefix` with 1 more element, the next number after those of `formulas` that start with `prefix`.

        The added element is 1 more than the largest element at that position among those numbers, or 1 if no number
        starts with `prefix`. With the number of a subcategory as `prefix`, the returned number is the next free source
        number; with the number of a source, the next free formula number.
        """
        taken = [formula.number[len(prefix)] for formula in formulas if formula.number[: len(prefix)] == prefix]
        return (*prefix, max(taken, default=0) + 1)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def build(
        cls, rows: list[RowsTableLine], formula_decisions: list[FormulaDecision], committed_table: "FormulasTable"
    ) -> "FormulasTable":
        """Return the formulas of the `new` rows, keeping every id of `committed_table`, for rows given in time order.

        A formula of `committed_table` keeps its id while it holds the same rows, and is retired once none of its rows
        is `new`; a retired formula that holds the same rows again becomes active again. Every other formula is
        appended: it gets the next free number of its source, and a source without a number gets the next free number
        of its subcategory. From an empty `committed_table`, `build` numbers the sources in time order and their
        formulas in the order of their rows.

        Raises:
            FormulaIdChangeError: If a change would change the id of a formula, which a person must resolve: a formula
                of `committed_table` that would join with another or split, that names a row that no longer exists,
                or whose source is now in another subcategory.
        """
        committed_formula_by_row_set = {frozenset(formula.row_ids): formula for formula in committed_table.formulas}
        committed_formula_by_row_id = {
            row_id: formula for formula in committed_table.formulas for row_id in formula.row_ids
        }
        problems = committed_table.find_problems(rows)
        # --- keep the committed ids -------------
        formulas = []
        formulas_to_append = []
        for source_id, formulas_of_source in cls._group_new_rows(rows, formula_decisions).items():
            for row_ids, variable_change in formulas_of_source:
                committed_formula = committed_formula_by_row_set.get(frozenset(row_ids))
                overlapping_ids = sorted(
                    {
                        committed_formula_by_row_id[row_id].formula_id
                        for row_id in row_ids
                        if row_id in committed_formula_by_row_id
                    }
                )
                if committed_formula is not None:
                    formulas.append(
                        replace(committed_formula, row_ids=row_ids, variable_change=variable_change, is_retired=False)
                    )
                elif overlapping_ids:
                    problems.append(f"the formula of {row_ids[0]} would join or split {', '.join(overlapping_ids)}")
                else:
                    formulas_to_append.append((source_id, row_ids, variable_change))
        # --- retire the rest --------------------
        # each committed formula that is not kept above holds no `new` row: a formula that holds one is kept above,
        # or reported as a join or split
        kept_numbers = {formula.number for formula in formulas}
        formulas += [
            replace(formula, is_retired=True)
            for formula in committed_table.formulas
            if formula.number not in kept_numbers
        ]
        if problems:
            raise FormulaIdChangeError(problems)
        # --- append the other formulas ----------
        # the numbers of retired formulas count as taken too, so that no number is given twice
        subcategory_number_by_source = {row.source_id: row.subcategory_number for row in rows}
        source_number_by_source = {formula.source_id: formula.number[:-1] for formula in formulas}
        for source_id, row_ids, variable_change in formulas_to_append:
            if source_id not in source_number_by_source:
                source_number_by_source[source_id] = cls._next_free_number(
                    subcategory_number_by_source[source_id], formulas
                )
            number = cls._next_free_number(source_number_by_source[source_id], formulas)
            formulas.append(FormulasTableLine(number, source_id, row_ids, variable_change, is_retired=False))
        return cls(tuple(sorted(formulas, key=lambda formula: formula.number)))

    @classmethod
    def read(cls, path: Path) -> "FormulasTable":
        """Return the formulas of `formulas.csv`, or an empty table if the file does not exist.

        Raises:
            DataFileError: If the columns are wrong, a line breaks its format, an id or a row is in more than 1 line,
                or a source has more than 1 number or a number more than 1 source.
        """
        if not path.exists():
            return cls(())
        else:
            with path.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames != FORMULA_COLUMNS:
                    raise DataFileError(f"{path.name}: the columns must be {FORMULA_COLUMNS}")
                formulas = [FormulasTableLine.from_csv_line(line, path.name) for line in reader]
            numbers = [formula.number for formula in formulas]
            row_ids = [row_id for formula in formulas for row_id in formula.row_ids]
            source_number_pairs = {(formula.source_id, formula.number[:-1]) for formula in formulas}
            n_sources = len({source_id for source_id, _ in source_number_pairs})
            n_source_numbers = len({source_number for _, source_number in source_number_pairs})
            if len(set(numbers)) < len(numbers) or len(set(row_ids)) < len(row_ids):
                raise DataFileError(f"{path.name}: an id or a row is in more than 1 line")
            elif n_sources < len(source_number_pairs) or n_source_numbers < len(source_number_pairs):
                raise DataFileError(f"{path.name}: a source has more than 1 number, or a number more than 1 source")
            else:
                return cls(tuple(formulas))


# ==================================================================================================
#  FormulasTableLine
# ==================================================================================================
@dataclass(frozen=True)
class FormulasTableLine:
    """A `FormulasTableLine` holds 1 line of `formulas.csv`: a formula's number, its source and its rows.

    `number` is the formula's place in the catalog's tree: category 1, the subcategory, the source and the formula,
    such as `(1, 4, 12, 3)`. `variable_change` is empty unless the formula's variable differs from that of its row's
    `f`. A retired formula keeps the rows that it held when it was retired, so that it becomes active again with its
    own id if those rows are `new` again.
    """

    number: tuple[int, ...]
    source_id: str
    row_ids: tuple[str, ...]
    variable_change: str
    is_retired: bool

    @property
    def formula_id(self) -> str:
        """Return the formula's id, its number with dots and an `f` prefix, such as `f1.4.12.3`."""
        return "f" + ".".join(str(part) for part in self.number)

    def to_csv_line(self) -> dict[str, str]:
        """Return the formula as 1 line of `formulas.csv`, keyed by column."""
        return {
            "formula_id": self.formula_id,
            "status": "retired" if self.is_retired else "active",
            "source_id": self.source_id,
            "row_ids": join_row_ids(self.row_ids),
            "variable_change": self.variable_change,
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_csv_line(cls, line: dict[str, str], file_name: str) -> "FormulasTableLine":
        """Return the formula of 1 line of `formulas.csv`.

        Raises:
            DataFileError: If the id is not `f` and 4 dotted positive integers, the status is unknown, or the line
                names no rows.
        """
        match = re.fullmatch(r"f([1-9][0-9]*(?:\.[1-9][0-9]*){3})", line["formula_id"])
        row_ids = tuple(split_row_ids(line["row_ids"]))
        if match is None or line["status"] not in FORMULA_STATUSES or not row_ids:
            raise DataFileError(f"{file_name}: the line of {line['formula_id']} breaks the format")
        else:
            return cls(
                number=tuple(int(part) for part in match.group(1).split(".")),
                source_id=line["source_id"],
                row_ids=row_ids,
                variable_change=line["variable_change"],
                is_retired=line["status"] == "retired",
            )
