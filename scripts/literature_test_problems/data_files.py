"""This module reads and writes the files of `data/literature_test_problems/`: source files, decisions and rows."""

import csv
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

# The subcategories of category 1 of sunnbear's formula catalog, which the `home` of each source names.
HOME_NAMES = {
    "1.1": "articles of solvers that sunnbear implements",
    "1.2": "articles of other solvers",
    "1.3": "public benchmark suites",
    "1.4": "textbooks",
}
FINAL_STATUSES = ("new", "duplicate", "variant", "extended")
# the status of a row that the script could not decide and that no decision covers yet
UNDECIDED = "judge"
# the separator between the row ids that 1 field names
ROW_ID_SEPARATOR = " | "


class DataFileError(ValueError):
    """A file of the data folder that does not follow its format."""


# ==================================================================================================
#  The data folder
# ==================================================================================================
@dataclass(frozen=True)
class DataFolder:
    """The data folder of the literature test problems, and the path of each of its files."""

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
    def rows_file(self) -> Path:
        """Return the generated table of every row with its automatic and final status."""
        return self.path / "rows.csv"

    @property
    def summary_file(self) -> Path:
        """Return the generated table of the sources."""
        return self.path / "summary.md"

    @property
    def timeline_file(self) -> Path:
        """Return the generated page that draws the sources in time order."""
        return self.path / "timeline.html"

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
    """1 test problem as its source gives it, with the row id that the other files use for it.

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
        """Return the row of 1 `[[rows]]` table of a source file, or raise `DataFileError`."""
        values = _take_strings(table, required={"key"}, optional=_ROW_FIELDS - {"key"}, where=where)
        if bool(values["f"]) == bool(values["f_description"]):
            raise DataFileError(f"{where}: needs exactly 1 of f and f_description")
        return cls(row_id=row_id, **values)


@dataclass(frozen=True)
class Relation:
    """A note on how the rows of 1 source relate to the rows of other sources."""

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
    """1 published source of test problems: its reference, where its rows come from, and its rows."""

    source_id: str
    title: str
    reference: str
    year: int
    home: str
    where_in_source: str
    transcribed_from: str
    rows_summary: str
    notes: str
    relations: tuple[Relation, ...]
    rows: tuple[SourceRow, ...]

    @property
    def time_order_key(self) -> tuple[int, str]:
        """Return the key that orders the sources in time: the year, then the id without its leading year."""
        return self.year, re.sub(r"^\d{4}_", "", self.source_id)

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
        values = _take_strings(data, required=_SOURCE_FIELDS, optional={"notes"}, where=path.name)
        if values["home"] not in HOME_NAMES:
            raise DataFileError(f"{path.name}: unknown home {values['home']!r}")
        stated = re.match(r"(\d+)\b", values["rows_summary"])
        if (int(stated.group(1)) if stated else 0) != len(rows):
            raise DataFileError(f"{path.name}: rows_summary does not start with the number of rows, {len(rows)}")
        return cls(source_id=path.stem, year=year, relations=relations, rows=rows, **values)

    @staticmethod
    def _rows_from_toml(source_id: str, tables: list[dict], file_name: str) -> tuple[SourceRow, ...]:
        """Return the rows of a source file, giving a key that the source repeats a suffix `#2`, `#3`, ..."""
        rows = []
        seen_keys: dict[str, int] = {}
        for i, table in enumerate(tables):
            key = str(table.get("key", "")).strip()
            seen_keys[key] = seen_keys.get(key, 0) + 1
            if seen_keys[key] > 1:
                row_id = f"{source_id}:{key}#{seen_keys[key]}"
            else:
                row_id = f"{source_id}:{key}"
            rows.append(SourceRow.from_toml(table, row_id, where=f"{file_name}, row {i + 1}"))
        return tuple(rows)


def read_sources(sources_dir: Path) -> list[Source]:
    """Return every source in time order, or raise `DataFileError` where a source file breaks the format."""
    sources = sorted(
        (Source.from_toml_file(path) for path in sources_dir.glob("*.toml")), key=lambda s: s.time_order_key
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
    """The status that the script finds for a row by comparing it with every earlier row."""

    status: str
    match_kind: str
    matches: str
    parse_note: str
    instances: int


@dataclass(frozen=True)
class FinalStatus:
    """A row's final status, the earlier rows that it matches, and the reason where a person decided it."""

    status: str
    earlier_rows: str
    reason: str

    @property
    def earlier_row_ids(self) -> list[str]:
        """Return the ids of the earlier rows."""
        return [row_id.strip() for row_id in self.earlier_rows.split(ROW_ID_SEPARATOR) if row_id.strip()]


def read_decisions(path: Path) -> dict[str, FinalStatus]:
    """Return the decided status of each row that `decisions.csv` names, or raise `DataFileError`."""
    decisions = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != _DECISION_COLUMNS:
            raise DataFileError(f"{path.name}: the columns must be {_DECISION_COLUMNS}")
        for line in reader:
            row_id = line["row_id"].strip()
            if row_id in decisions:
                raise DataFileError(f"{path.name}: {row_id} is decided twice")
            elif line["status"] not in FINAL_STATUSES:
                raise DataFileError(f"{path.name}: {row_id} has unknown status {line['status']!r}")
            else:
                decisions[row_id] = FinalStatus(line["status"], line["earlier_rows"].strip(), line["reason"].strip())
    return decisions


@dataclass(frozen=True)
class RowStatus:
    """A row of the survey with its automatic and final status: 1 line of `rows.csv`."""

    row_id: str
    year: int
    home: str
    f: str
    f_description: str
    parameters: str
    interval: str
    automatic: AutomaticStatus
    final: FinalStatus

    @property
    def source_id(self) -> str:
        """Return the id of the row's source."""
        return self.row_id.split(":", 1)[0]

    @property
    def key(self) -> str:
        """Return the row's key within its source, with the suffix of a repeated key."""
        return self.row_id.split(":", 1)[1]

    def to_csv_line(self) -> dict[str, str]:
        """Return the row as 1 line of `rows.csv`, keyed by column."""
        return {
            "row_id": self.row_id,
            "year": str(self.year),
            "home": self.home,
            "f": self.f,
            "f_description": self.f_description,
            "parameters": self.parameters,
            "interval": self.interval,
            "parse_note": self.automatic.parse_note,
            "instances": str(self.automatic.instances),
            "auto_status": self.automatic.status,
            "match_kind": self.automatic.match_kind,
            "matches": self.automatic.matches,
            "status": self.final.status,
            "earlier_rows": self.final.earlier_rows,
            "reason": self.final.reason,
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_csv_line(cls, line: dict[str, str]) -> "RowStatus":
        """Return the row of 1 line of `rows.csv`."""
        return cls(
            row_id=line["row_id"],
            year=int(line["year"]),
            home=line["home"],
            f=line["f"],
            f_description=line["f_description"],
            parameters=line["parameters"],
            interval=line["interval"],
            automatic=AutomaticStatus(
                status=line["auto_status"],
                match_kind=line["match_kind"],
                matches=line["matches"],
                parse_note=line["parse_note"],
                instances=int(line["instances"]),
            ),
            final=FinalStatus(status=line["status"], earlier_rows=line["earlier_rows"], reason=line["reason"]),
        )

    @classmethod
    def from_source_row(
        cls, source: Source, row: SourceRow, automatic: AutomaticStatus, final: FinalStatus
    ) -> "RowStatus":
        """Return a source row with its statuses."""
        return cls(
            row_id=row.row_id,
            year=source.year,
            home=source.home,
            f=row.f,
            f_description=row.f_description,
            parameters=row.parameters,
            interval=row.interval,
            automatic=automatic,
            final=final,
        )


def read_rows_table(path: Path) -> list[RowStatus]:
    """Return the rows of `rows.csv`, in time order."""
    with path.open(encoding="utf-8", newline="") as f:
        return [RowStatus.from_csv_line(line) for line in csv.DictReader(f)]


def write_rows_table(path: Path, rows: list[RowStatus]) -> None:
    """Write `rows.csv`, with Unix line endings."""
    lines = [row.to_csv_line() for row in rows]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(lines[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(lines)


# ==================================================================================================
#  Helpers
# ==================================================================================================
_SOURCE_FIELDS = {"title", "reference", "home", "where_in_source", "transcribed_from", "rows_summary"}
_ROW_FIELDS = {"key", "f", "f_description", "name", "parameters", "interval", "also_in", "notes"}
_DECISION_COLUMNS = ["row_id", "status", "earlier_rows", "reason"]


def _take_strings(table: dict, required: set[str], optional: set[str], where: str) -> dict[str, str]:
    """Return the string fields of a TOML table, stripped, with "" for each missing optional field, or raise."""
    unknown = sorted(set(table) - required - optional)
    missing = sorted(required - set(table))
    if unknown or missing:
        raise DataFileError(f"{where}: unknown fields {unknown}, missing fields {missing}")
    not_strings = sorted(name for name, value in table.items() if not isinstance(value, str))
    if not_strings:
        raise DataFileError(f"{where}: fields {not_strings} must be strings")
    return {name: table.get(name, "").strip() for name in required | optional}
