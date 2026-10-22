"""This module reads and writes the files of `data/literature_test_problems/`: source files, decisions and rows."""

import csv
import re
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

# SUBCATEGORY_DESCRIPTIONS describes each subcategory of category 1 of sunnbear's formula catalog; the
# `subcategory` of each source is 1 of its keys.
SUBCATEGORY_DESCRIPTIONS = {
    "1.1": "articles of solvers that sunnbear implements",
    "1.2": "articles of other solvers",
    "1.3": "public benchmark suites",
    "1.4": "textbooks",
}
DECIDED_STATUSES = ("new", "duplicate", "incomplete")
# UNDECIDED is the status of a row that the script could not decide and that no decision covers yet.
UNDECIDED = "undecided"
# ROW_ID_SEPARATOR separates the row ids in 1 field.
ROW_ID_SEPARATOR = " | "
# DECISION_COLUMNS are the columns of `decisions.csv`, in order.
DECISION_COLUMNS = ["row_id", "status", "duplicate_of", "derived_from", "reason"]
# FORMULA_DECISION_COLUMNS are the columns of `formula_decisions.csv`, in order.
FORMULA_DECISION_COLUMNS = ["row_ids", "variable_change", "reason"]


class DataFileError(ValueError):
    """A `DataFileError` reports a file of the data folder that does not follow its format."""


# ==================================================================================================
#  The data folder
# ==================================================================================================
@dataclass(frozen=True)
class DataFolder:
    """A `DataFolder` holds the path of the literature test problems' data folder, and gives the path of each file."""

    path: Path

    @property
    def sources_dir(self) -> Path:
        """Return the folder of the source files, 1 TOML file per source."""
        return self.path / "sources"

    @property
    def decisions_file(self) -> Path:
        """Return the curated file of the statuses that a person decided."""
        return self.path / "decisions.csv"

    @property
    def formula_decisions_file(self) -> Path:
        """Return the curated file of the formulas that hold several rows or change a row's variable."""
        return self.path / "formula_decisions.csv"

    @property
    def rows_file(self) -> Path:
        """Return the generated table of every row with its automatic and final status."""
        return self.path / "rows.csv"

    @property
    def formulas_file(self) -> Path:
        """Return the generated table that maps each formula id to its rows."""
        return self.path / "formulas.csv"

    @property
    def summary_file(self) -> Path:
        """Return the generated table of the sources."""
        return self.path / "summary.md"

    @property
    def timeline_file(self) -> Path:
        """Return the generated page that draws the sources in time order."""
        return self.path / "timeline.html"

    @property
    def readme_file(self) -> Path:
        """Return the README, which defines the format of every file."""
        return self.path / "README.md"

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def in_repo(cls) -> "DataFolder":
        """Return the data folder of the repo that holds this script."""
        return cls(Path(__file__).resolve().parents[2] / "data" / "literature_test_problems")


# ==================================================================================================
#  Source files
# ==================================================================================================
@dataclass(frozen=True)
class SourceRow:
    """A `SourceRow` holds 1 test problem as its source gives it, with the row id that the other files use for it.

    Exactly 1 of `f` and `f_description` is set: `f` holds the row's function as 1 expression, and
    `f_description` describes a function that 1 expression does not give, such as a piecewise function.
    """

    row_id: str
    key: str
    f: str
    f_description: str
    name: str
    parameters: str
    interval: str
    also_in: str
    notes: str

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_toml(cls, table: dict, row_id: str, where: str) -> "SourceRow":
        """Return the row of 1 `[[rows]]` table of a source file, or raise `DataFileError`.

        `where` names the table's place in its file, which starts each error message.
        """
        values = _read_string_fields(table, required={"key"}, optional=_ROW_FIELDS - {"key"}, where=where)
        if bool(values["f"]) == bool(values["f_description"]):
            raise DataFileError(f"{where}: needs exactly 1 of f and f_description")
        else:
            return cls(row_id=row_id, **values)


@dataclass(frozen=True)
class Relation:
    """A `Relation` notes how the rows of 1 source relate to the rows of other sources."""

    source_ids: tuple[str, ...]
    text: str

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_toml(cls, table: dict, where: str) -> "Relation":
        """Return the relation of 1 `[[relations]]` table of a source file, or raise `DataFileError`."""
        if set(table) != {"sources", "text"}:
            raise DataFileError(f"{where}: a relation has exactly the fields sources and text")
        source_ids, text = table["sources"], table["text"]
        if not isinstance(source_ids, list) or not source_ids or not all(isinstance(s, str) for s in source_ids):
            raise DataFileError(f"{where}: sources must be a non-empty list of source ids")
        elif not isinstance(text, str) or not text.strip():
            raise DataFileError(f"{where}: text must be a non-empty string")
        else:
            return cls(source_ids=tuple(source_ids), text=text.strip())


@dataclass(frozen=True)
class Source:
    """A `Source` holds 1 published source of test problems: its reference, where its rows come from, and its rows."""

    source_id: str
    title: str
    reference: str
    year: int
    subcategory: str
    where_in_source: str
    transcribed_from: str
    rows_summary: str
    notes: str
    relations: tuple[Relation, ...]
    rows: tuple[SourceRow, ...]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _rows_from_toml(source_id: str, tables: list[dict], file_name: str) -> tuple[SourceRow, ...]:
        """Return the rows of a source file, or raise `DataFileError` if 2 rows have the same key.

        A row's id is fixed by its key alone, not by its position, so that adding a row never changes the id of
        another row; a key that the source repeats is written with a suffix `#2`, `#3`, ... in the file.
        """
        rows = []
        seen_keys: set[str] = set()
        for i, table in enumerate(tables):
            key = str(table.get("key", "")).strip()
            if key in seen_keys:
                raise DataFileError(f"{file_name}, row {i + 1}: the key {key!r} is in more than 1 row")
            else:
                seen_keys.add(key)
                rows.append(SourceRow.from_toml(table, f"{source_id}:{key}", where=f"{file_name}, row {i + 1}"))
        return tuple(rows)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_toml_file(cls, path: Path) -> "Source":
        """Return the source of 1 source file, or raise `DataFileError` where the file breaks the format."""
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            raise DataFileError(f"{path.name}: {error}") from error
        year = data.pop("year", None)
        if not isinstance(year, int):
            raise DataFileError(f"{path.name}: year must be an integer")
        relations = tuple(
            Relation.from_toml(table, where=f"{path.name}, relation {i + 1}")
            for i, table in enumerate(data.pop("relations", []))
        )
        rows = cls._rows_from_toml(path.stem, data.pop("rows", []), path.name)
        values = _read_string_fields(data, required=_SOURCE_FIELDS, optional={"notes"}, where=path.name)
        if values["subcategory"] not in SUBCATEGORY_DESCRIPTIONS:
            raise DataFileError(f"{path.name}: unknown subcategory {values['subcategory']!r}")
        stated = re.match(r"(\d+)\b", values["rows_summary"])
        if stated:
            n_stated_rows = int(stated.group(1))
        else:
            n_stated_rows = 0
        if n_stated_rows != len(rows):
            raise DataFileError(f"{path.name}: rows_summary does not start with the number of rows, {len(rows)}")
        else:
            return cls(source_id=path.stem, year=year, relations=relations, rows=rows, **values)


def read_sources(sources_dir: Path) -> list[Source]:
    """Return every source in time order, or raise `DataFileError` where a source file breaks the format."""
    # the sources sort in time order: by year, then by id without its leading year
    sources = sorted(
        (Source.from_toml_file(path) for path in sources_dir.glob("*.toml")),
        key=lambda s: (s.year, re.sub(r"^\d{4}_", "", s.source_id)),
    )
    known = {source.source_id for source in sources}
    for source in sources:
        for relation in source.relations:
            unknown = sorted(set(relation.source_ids) - known)
            if unknown:
                raise DataFileError(f"{source.source_id}.toml: a relation names unknown sources {unknown}")
    return sources


# ==================================================================================================
#  Statuses, decisions and the table of rows
# ==================================================================================================
@dataclass(frozen=True)
class AutomaticStatus:
    """An `AutomaticStatus` holds the status that the script finds for a row by comparing it with every earlier row.

    `matches` holds the matched row ids joined by `ROW_ID_SEPARATOR`, and `match_kind` names the comparisons that
    found them; for an `incomplete` row, `match_kind` names why the row is incomplete instead, such as "no interval",
    and for an undecided row why a person must decide, such as "no test function". `n_instances` is 0 for a row
    whose f does not parse.
    """

    status: str
    match_kind: str
    matches: str
    parse_note: str
    n_instances: int


@dataclass(frozen=True)
class FinalStatus:
    """A `FinalStatus` holds a row's final status, the earlier rows that it names, and the reason for the status.

    A `duplicate` names, in `duplicate_of`, the earlier rows that already give its test functions; a `new` or
    `incomplete` row names, in `derived_from`, the earlier rows whose function it copies or changes. Each field joins
    its row ids by `ROW_ID_SEPARATOR`.
    """

    status: str
    duplicate_of: str
    derived_from: str
    reason: str

    @property
    def duplicate_of_ids(self) -> list[str]:
        """Return the ids of the rows in `duplicate_of`."""
        return split_row_ids(self.duplicate_of)

    @property
    def derived_from_ids(self) -> list[str]:
        """Return the ids of the rows in `derived_from`."""
        return split_row_ids(self.derived_from)

    @property
    def named_row_ids(self) -> list[str]:
        """Return the ids of every earlier row that the row names, in `duplicate_of` or in `derived_from`."""
        return [*self.duplicate_of_ids, *self.derived_from_ids]

    def find_status_problems(self, row_id: str) -> list[str]:
        """Return the first problem of the status and of its fields `duplicate_of`, `derived_from` and `reason`.

        The result is a list of at most 1 problem. `row_id` is the id of the row that has this status; each problem
        starts with it.
        """
        if self.status == UNDECIDED:
            return [f"{row_id} needs a decision in decisions.csv"]
        elif self.status not in DECIDED_STATUSES:
            return [f"{row_id} has an unknown status, {self.status}"]
        elif self.status == "duplicate" and not self.duplicate_of:
            return [f"{row_id} is duplicate but names no row in duplicate_of"]
        elif self.status == "duplicate" and self.derived_from:
            return [f"{row_id} is duplicate but names rows in derived_from"]
        elif self.status != "duplicate" and self.duplicate_of:
            return [f"{row_id} is {self.status} but names rows in duplicate_of"]
        elif self.status == "incomplete" and not self.reason:
            return [f"{row_id} is incomplete but gives no reason"]
        else:
            return []

    def find_named_row_problems(
        self, row_id: str, final_statuses: dict[str, "FinalStatus"], position: dict[str, int]
    ) -> list[str]:
        """Return the problems of the rows that the row names: unknown or not earlier, or in `duplicate_of` not `new`.

        `row_id` is the id of the row that has this status; `position` holds each row's index in time order.
        """
        problems = []
        for named_row_id in self.named_row_ids:
            if named_row_id not in position:
                problems.append(f"{row_id} names an unknown row, {named_row_id}")
            elif position[named_row_id] >= position[row_id]:
                problems.append(f"{row_id} names a row that is not earlier, {named_row_id}")
        for named_row_id in self.duplicate_of_ids:
            if named_row_id in final_statuses and final_statuses[named_row_id].status != "new":
                problems.append(f"{row_id} is a duplicate of a row that is not new, {named_row_id}")
        return problems

    def with_first_appearances(self, resolved_statuses: dict[str, "FinalStatus"]) -> "FinalStatus":
        """Return the status with each named duplicate replaced by the rows in its `duplicate_of`.

        `resolved_statuses` holds the final statuses of the earlier rows, which already name their own first
        appearances.
        """
        return FinalStatus(
            self.status,
            join_row_ids(self._first_appearances(self.duplicate_of_ids, resolved_statuses)),
            join_row_ids(self._first_appearances(self.derived_from_ids, resolved_statuses)),
            self.reason,
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _first_appearances(row_ids: list[str], resolved_statuses: dict[str, "FinalStatus"]) -> list[str]:
        """Return the row ids with each resolved duplicate replaced by the rows in its `duplicate_of`."""
        first_appearances = []
        for row_id in row_ids:
            if row_id in resolved_statuses and resolved_statuses[row_id].status == "duplicate":
                first_appearances.extend(resolved_statuses[row_id].duplicate_of_ids)
            else:
                first_appearances.append(row_id)
        return first_appearances

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_automatic_status(cls, automatic_status: AutomaticStatus) -> "FinalStatus":
        """Return the final status that an automatic status gives a row without a decision."""
        status, matches = automatic_status.status, automatic_status.matches
        if status == "duplicate":
            return cls(status, duplicate_of=matches, derived_from="", reason="")
        elif status == "new":
            return cls(status, duplicate_of="", derived_from=matches, reason="")
        elif status == "incomplete":
            return cls(status, duplicate_of="", derived_from=matches, reason=automatic_status.match_kind)
        else:
            return cls(status, duplicate_of="", derived_from="", reason="")


def read_decisions(path: Path) -> dict[str, FinalStatus]:
    """Return the decided status of each row that `decisions.csv` names, or raise `DataFileError`."""
    decisions = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != DECISION_COLUMNS:
            raise DataFileError(f"{path.name}: the columns must be {DECISION_COLUMNS}")
        for line in reader:
            row_id = line["row_id"].strip()
            if row_id in decisions:
                raise DataFileError(f"{path.name}: {row_id} is decided twice")
            elif line["status"] not in DECIDED_STATUSES:
                raise DataFileError(f"{path.name}: {row_id} has unknown status {line['status']!r}")
            else:
                decisions[row_id] = FinalStatus(
                    line["status"], line["duplicate_of"].strip(), line["derived_from"].strip(), line["reason"].strip()
                )
    return decisions


@dataclass(frozen=True)
class RowsTableLine:
    """A `RowsTableLine` holds 1 line of `rows.csv`: a row of the survey with its automatic and final status."""

    row_id: str
    year: int
    subcategory: str
    f: str
    f_description: str
    parameters: str
    interval: str
    automatic_status: AutomaticStatus
    final_status: FinalStatus

    @property
    def source_id(self) -> str:
        """Return the id of the row's source."""
        return source_id_of_row_id(self.row_id)

    @property
    def key(self) -> str:
        """Return the row's key within its source, with the suffix of a repeated key."""
        return self.row_id.split(":", 1)[1]

    @property
    def subcategory_number(self) -> tuple[int, ...]:
        """Return the subcategory as a taxonomy number, such as `(1, 4)` for `1.4`."""
        return tuple(int(part) for part in self.subcategory.split("."))

    def to_csv_line(self) -> dict[str, str]:
        """Return the row as 1 line of `rows.csv`, keyed by column."""
        return {
            "row_id": self.row_id,
            "year": str(self.year),
            "subcategory": self.subcategory,
            "f": self.f,
            "f_description": self.f_description,
            "parameters": self.parameters,
            "interval": self.interval,
            "parse_note": self.automatic_status.parse_note,
            "n_instances": str(self.automatic_status.n_instances),
            "automatic_status": self.automatic_status.status,
            "match_kind": self.automatic_status.match_kind,
            "matches": self.automatic_status.matches,
            "status": self.final_status.status,
            "duplicate_of": self.final_status.duplicate_of,
            "derived_from": self.final_status.derived_from,
            "reason": self.final_status.reason,
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_csv_line(cls, line: dict[str, str]) -> "RowsTableLine":
        """Return the row of 1 line of `rows.csv`."""
        return cls(
            row_id=line["row_id"],
            year=int(line["year"]),
            subcategory=line["subcategory"],
            f=line["f"],
            f_description=line["f_description"],
            parameters=line["parameters"],
            interval=line["interval"],
            automatic_status=AutomaticStatus(
                status=line["automatic_status"],
                match_kind=line["match_kind"],
                matches=line["matches"],
                parse_note=line["parse_note"],
                n_instances=int(line["n_instances"]),
            ),
            final_status=FinalStatus(
                status=line["status"],
                duplicate_of=line["duplicate_of"],
                derived_from=line["derived_from"],
                reason=line["reason"],
            ),
        )

    @classmethod
    def from_source_row(
        cls, source: Source, row: SourceRow, automatic_status: AutomaticStatus, final_status: FinalStatus
    ) -> "RowsTableLine":
        """Return a source row with its statuses."""
        return cls(
            row_id=row.row_id,
            year=source.year,
            subcategory=source.subcategory,
            f=row.f,
            f_description=row.f_description,
            parameters=row.parameters,
            interval=row.interval,
            automatic_status=automatic_status,
            final_status=final_status,
        )


def read_rows_table(path: Path) -> list[RowsTableLine]:
    """Return the rows of `rows.csv`, in time order."""
    with path.open(encoding="utf-8", newline="") as f:
        return [RowsTableLine.from_csv_line(line) for line in csv.DictReader(f)]


def write_rows_table(path: Path, rows: list[RowsTableLine]) -> None:
    """Write `rows.csv`, with Unix line endings; `rows` must not be empty."""
    lines = [row.to_csv_line() for row in rows]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(lines[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(lines)


# ==================================================================================================
#  Formula decisions
# ==================================================================================================
@dataclass(frozen=True)
class FormulaDecision:
    """A `FormulaDecision` holds 1 line of `formula_decisions.csv`: the rows of 1 formula, decided by a person.

    Without a decision, each `new` row is a formula of its own. A decision does 1 or both of these:

    - it puts several rows of 1 source that are obviously 1 function into 1 formula;
    - it gives 1 row's formula a different variable from that of the row's `f`, and `variable_change` describes the
      new variable.
    """

    row_ids: tuple[str, ...]
    variable_change: str
    reason: str

    def find_problems(self, status_by_row_id: dict[str, str]) -> list[str]:
        """Return the problems of the decision's rows: unknown, not `new`, or of more than 1 source.

        `status_by_row_id` holds the final status of every row.
        """
        problems = []
        for row_id in self.row_ids:
            if row_id not in status_by_row_id:
                problems.append(f"formula_decisions.csv names an unknown row, {row_id}")
            elif status_by_row_id[row_id] != "new":
                problems.append(f"formula_decisions.csv names a row that is not new, {row_id}")
        source_ids = {source_id_of_row_id(row_id) for row_id in self.row_ids}
        if len(source_ids) > 1:
            problems.append(f"formula_decisions.csv joins rows of {len(source_ids)} sources, {self.row_ids[0]}")
        return problems

    @staticmethod
    def find_all_problems(formula_decisions: list["FormulaDecision"], rows: list[RowsTableLine]) -> list[str]:
        """Return the problems of every decision, for the rows of `rows.csv` with their final statuses."""
        status_by_row_id = {row.row_id: row.final_status.status for row in rows}
        return [problem for decision in formula_decisions for problem in decision.find_problems(status_by_row_id)]

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_csv_line(cls, line: dict[str, str], file_name: str) -> "FormulaDecision":
        """Return the decision of 1 line of `formula_decisions.csv`, or raise `DataFileError`.

        Raises:
            DataFileError: If the line names no rows, gives no reason, or names 1 row and no variable change.
        """
        decision = cls(tuple(split_row_ids(line["row_ids"])), line["variable_change"].strip(), line["reason"].strip())
        if not decision.row_ids or not decision.reason:
            raise DataFileError(f"{file_name}: each line needs row_ids and a reason")
        elif len(decision.row_ids) == 1 and not decision.variable_change:
            raise DataFileError(f"{file_name}: {decision.row_ids[0]} is alone in its line but changes no variable")
        else:
            return decision


def read_formula_decisions(path: Path) -> list[FormulaDecision]:
    """Return the decisions of `formula_decisions.csv`, or raise `DataFileError`.

    Raises:
        DataFileError: If the columns are wrong, a line names no rows or gives no reason, a line of 1 row gives no
            variable change, or a row is in more than 1 line.
    """
    formula_decisions = []
    seen_row_ids: set[str] = set()
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FORMULA_DECISION_COLUMNS:
            raise DataFileError(f"{path.name}: the columns must be {FORMULA_DECISION_COLUMNS}")
        for line in reader:
            formula_decision = FormulaDecision.from_csv_line(line, path.name)
            row_ids = formula_decision.row_ids
            repeated = [r for r in row_ids if r in seen_row_ids or row_ids.count(r) > 1]
            if repeated:
                raise DataFileError(f"{path.name}: {repeated[0]} is in more than 1 line")
            else:
                formula_decisions.append(formula_decision)
                seen_row_ids.update(row_ids)
    return formula_decisions


# ==================================================================================================
#  Helpers
# ==================================================================================================
_SOURCE_FIELDS = {"title", "reference", "subcategory", "where_in_source", "transcribed_from", "rows_summary"}
_ROW_FIELDS = {"key", "f", "f_description", "name", "parameters", "interval", "also_in", "notes"}


def join_row_ids(row_ids: Iterable[str | None]) -> str:
    """Join the distinct row ids, in the order that each first occurs, into 1 field that `FinalStatus` splits again."""
    return ROW_ID_SEPARATOR.join(dict.fromkeys(r for r in row_ids if r))


def split_row_ids(field: str) -> list[str]:
    """Return the row ids of 1 field that `join_row_ids` built, or that a person wrote in the same form."""
    return [row_id.strip() for row_id in field.split(ROW_ID_SEPARATOR) if row_id.strip()]


def source_id_of_row_id(row_id: str) -> str:
    """Return the id of the source that a row id names, the part before its first `:`."""
    return row_id.split(":", 1)[0]


def _read_string_fields(table: dict, required: set[str], optional: set[str], where: str) -> dict[str, str]:
    """Return the string fields of a TOML table, stripped, with "" for each missing optional field.

    Raises:
        DataFileError: If the table lacks a required field, has an unknown field, or a field is not a string.
    """
    unknown = sorted(set(table) - required - optional)
    missing = sorted(required - set(table))
    if unknown or missing:
        raise DataFileError(f"{where}: unknown fields {unknown}, missing fields {missing}")
    not_strings = sorted(name for name, value in table.items() if not isinstance(value, str))
    if not_strings:
        raise DataFileError(f"{where}: fields {not_strings} must be strings")
    else:
        return {name: table.get(name, "").strip() for name in required | optional}
