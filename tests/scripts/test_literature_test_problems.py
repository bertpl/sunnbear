"""The generated files of `data/literature_test_problems/` agree with the folder's source files and decisions.

The tests use the script's modules that need only the standard library; the row comparison in `matching`, which
needs sympy, is not run here, because another sympy version could change a match.
"""

import csv
import importlib
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest

_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "scripts" / "literature_test_problems"


# ==================================================================================================
#  Fixtures
# ==================================================================================================
@pytest.fixture(scope="module")
def script_modules() -> dict[str, ModuleType]:
    """Return the script's modules that need only the standard library, keyed by name.

    They are imported by path, because the `scripts` folder is not an installed package.
    """
    spec = importlib.util.spec_from_file_location(
        "literature_test_problems", _PACKAGE_DIR / "__init__.py", submodule_search_locations=[str(_PACKAGE_DIR)]
    )
    package = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = package
    spec.loader.exec_module(package)
    return {
        name: importlib.import_module(f"literature_test_problems.{name}")
        for name in ("data_files", "statuses", "overview", "formulas")
    }


@pytest.fixture(scope="module")
def folder(script_modules):
    """Return the repo's data folder."""
    return script_modules["data_files"].DataFolder.in_repo()


@pytest.fixture(scope="module")
def sources(script_modules, folder):
    """Return the sources of the source files, in time order."""
    return script_modules["data_files"].read_sources(folder.sources_dir)


@pytest.fixture(scope="module")
def rows(script_modules, folder):
    """Return the rows of the committed `rows.csv`."""
    return script_modules["data_files"].read_rows_table(folder.rows_file)


@pytest.fixture(scope="module")
def decisions(script_modules, folder):
    """Return the committed decisions."""
    return script_modules["data_files"].read_decisions(folder.decisions_file)


@pytest.fixture(scope="module")
def formula_decisions(script_modules, folder):
    """Return the committed decisions of the formulas."""
    return script_modules["data_files"].read_formula_decisions(folder.formula_decisions_file)


@pytest.fixture(scope="module")
def committed_formulas(script_modules, folder):
    """Return the committed `formulas.csv` as a list of (formula id, source id, row ids)."""
    with folder.formulas_file.open(encoding="utf-8", newline="") as f:
        return [
            (line["formula_id"], line["source_id"], script_modules["data_files"].split_row_ids(line["row_ids"]))
            for line in csv.DictReader(f)
        ]


# ==================================================================================================
#  The committed files
# ==================================================================================================
def test_rows_table_holds_the_rows_of_the_source_files(sources, rows):
    """`rows.csv` holds exactly the rows of the source files, in time order."""
    # --- arrange / act ----------------
    from_sources = [
        (row.row_id, source.year, source.subcategory, row.f, row.f_description, row.parameters, row.interval)
        for source in sources
        for row in source.rows
    ]
    from_table = [(r.row_id, r.year, r.subcategory, r.f, r.f_description, r.parameters, r.interval) for r in rows]

    # --- assert -----------------------
    assert from_table == from_sources


def test_rows_table_applies_every_decision(script_modules, rows, decisions):
    """The final statuses in `rows.csv` equal its automatic statuses with every decision applied."""
    # --- arrange ----------------------
    automatic_statuses = {row.row_id: row.automatic_status for row in rows}

    # --- act --------------------------
    final_statuses = script_modules["statuses"].decide_final_statuses(automatic_statuses, decisions)

    # --- assert -----------------------
    assert {row.row_id: row.final_status for row in rows} == final_statuses


def test_rows_table_has_no_problems(script_modules, rows, decisions):
    """The final statuses in `rows.csv` have no problems: every row is decided and names only earlier rows."""
    # --- act --------------------------
    problems = script_modules["statuses"].find_problems({row.row_id: row.final_status for row in rows}, decisions)

    # --- assert -----------------------
    assert problems == []


@pytest.mark.parametrize(
    "file_property, build_method",
    [
        ("summary_file", "summary_markdown"),
        ("timeline_file", "timeline_html"),
    ],
)
def test_overview_file_matches_its_inputs(script_modules, folder, sources, rows, file_property, build_method):
    """Each overview file equals what the script builds from the source files and `rows.csv`."""
    # --- arrange / act ----------------
    overview = script_modules["overview"].Overview.build(sources, rows)
    built = getattr(overview, build_method)()

    # --- assert -----------------------
    assert built == getattr(folder, file_property).read_text(encoding="utf-8")


def test_formulas_file_matches_its_inputs(script_modules, folder, rows, formula_decisions):
    """`formulas.csv` equals what the script builds from `rows.csv` and `formula_decisions.csv`."""
    # --- arrange / act ----------------
    built = script_modules["formulas"].FormulasTable.build(rows, formula_decisions).csv_text()

    # --- assert -----------------------
    assert built == folder.formulas_file.read_text(encoding="utf-8")


def test_formulas_file_holds_every_new_row_once(rows, committed_formulas):
    """`formulas.csv` names every `new` row exactly once, and no other row."""
    # --- arrange / act ----------------
    named_row_ids = [row_id for _, _, row_ids in committed_formulas for row_id in row_ids]
    new_row_ids = [row.row_id for row in rows if row.final_status.status == "new"]

    # --- assert -----------------------
    assert sorted(named_row_ids) == sorted(new_row_ids)


def test_formulas_file_keeps_each_formula_within_its_source(script_modules, committed_formulas):
    """Every row of a formula in `formulas.csv` comes from the formula's own source."""
    # --- arrange / act ----------------
    rows_of_other_sources = [
        (formula_id, row_id)
        for formula_id, source_id, row_ids in committed_formulas
        for row_id in row_ids
        if script_modules["data_files"].source_id_of_row(row_id) != source_id
    ]

    # --- assert -----------------------
    assert rows_of_other_sources == []


def test_formula_decisions_have_no_problems(script_modules, rows, formula_decisions):
    """Every line of `formula_decisions.csv` names known `new` rows of 1 source."""
    # --- arrange / act ----------------
    problems = script_modules["data_files"].FormulaDecision.find_all_problems(formula_decisions, rows)

    # --- assert -----------------------
    assert problems == []


def test_readme_lists_every_subcategory(script_modules, folder):
    """The README's list of subcategories equals `SUBCATEGORY_DESCRIPTIONS`."""
    # --- arrange / act ----------------
    readme = folder.readme_file.read_text(encoding="utf-8")
    listed = dict(re.findall(r"^- `(\d\.\d)`: (.+)$", readme, flags=re.MULTILINE))

    # --- assert -----------------------
    assert listed == script_modules["data_files"].SUBCATEGORY_DESCRIPTIONS


def test_readme_lists_every_status(script_modules, folder):
    """The README's lists of statuses name exactly the decided statuses and the status of an undecided row."""
    # --- arrange / act ----------------
    data_files = script_modules["data_files"]
    readme = folder.readme_file.read_text(encoding="utf-8")
    statuses_section = readme.split("\n## Statuses\n")[1].split("\n## ")[0]
    listed = set(re.findall(r"^- \*\*`(\w+)`:\*\*", statuses_section, flags=re.MULTILINE))

    # --- assert -----------------------
    assert listed == {*data_files.DECIDED_STATUSES, data_files.UNDECIDED}


@pytest.mark.parametrize(
    "file_name, module_name, columns_name",
    [
        ("decisions.csv", "data_files", "DECISION_COLUMNS"),
        ("formula_decisions.csv", "data_files", "FORMULA_DECISION_COLUMNS"),
        ("formulas.csv", "formulas", "FORMULA_COLUMNS"),
    ],
)
def test_readme_lists_every_column(script_modules, folder, file_name, module_name, columns_name):
    """The README's list of the columns of each CSV file equals the columns that the script reads or writes."""
    # --- arrange / act ----------------
    readme = folder.readme_file.read_text(encoding="utf-8")
    pattern = rf"(?:^|\. )`{re.escape(file_name)}` [^\n]*?with the columns (.+?)\."
    columns_sentence = re.search(pattern, readme, re.MULTILINE).group(1)
    listed = re.findall(r"`(\w+)`", columns_sentence)

    # --- assert -----------------------
    assert listed == getattr(script_modules[module_name], columns_name)


def test_timeline_template_counts_every_status(script_modules):
    """The timeline's line of row counts names exactly the decided statuses and the status of an undecided row."""
    # --- arrange / act ----------------
    data_files = script_modules["data_files"]
    template = script_modules["overview"].TIMELINE_TEMPLATE.read_text(encoding="utf-8")
    counts_line = re.search(r"\$\{c\.rows\} rows: (.*)</p>", template).group(1)
    listed = set(re.findall(r"\$\{c\.(\w+)\}", counts_line))

    # --- assert -----------------------
    assert listed == {*data_files.DECIDED_STATUSES, data_files.UNDECIDED}


# ==================================================================================================
#  The rules of the final statuses
# ==================================================================================================
@pytest.mark.parametrize(
    "status, field_name",
    [
        ("duplicate", "duplicate_of"),  # a duplicate of a duplicate names the first appearance
        ("new", "derived_from"),  # a row derived from a duplicate names the first appearance too
        ("incomplete", "derived_from"),
    ],
)
def test_decide_final_statuses_names_the_first_appearance(script_modules, status, field_name):
    """A row that names a duplicate, in either field, names that duplicate's first appearance instead."""
    # --- arrange ----------------------
    data_files = script_modules["data_files"]
    automatic_statuses = {
        "s:1": data_files.AutomaticStatus("new", "", "", "", 1),
        "s:2": data_files.AutomaticStatus("duplicate", "structure", "s:1", "", 1),
        "s:3": data_files.AutomaticStatus(status, "structure", "s:2", "", 1),
    }

    # --- act --------------------------
    final_statuses = script_modules["statuses"].decide_final_statuses(automatic_statuses, decisions={})

    # --- assert -----------------------
    assert getattr(final_statuses["s:3"], field_name) == "s:1"


@pytest.mark.parametrize(
    "status, duplicate_of, derived_from, reason, expected_problems",
    [
        ("duplicate", "s:1", "", "", []),
        ("duplicate", "s:2", "", "", ["s:3 is a duplicate of a row that is not new, s:2"]),
        ("duplicate", "", "", "", ["s:3 is duplicate but names no row in duplicate_of"]),
        ("duplicate", "s:1", "s:2", "", ["s:3 is duplicate but names rows in derived_from"]),
        ("new", "s:1", "", "", ["s:3 is new but names rows in duplicate_of"]),
        ("new", "", "s:2", "", []),
        ("incomplete", "", "s:1", "", ["s:3 is incomplete but gives no reason"]),
        ("incomplete", "", "s:1", "no interval", []),
        ("new", "", "s:4", "", ["s:3 names a row that is not earlier, s:4"]),
        ("undecided", "", "", "", ["s:3 needs a decision in decisions.csv"]),
    ],
)
def test_find_problems_checks_each_status(
    script_modules, status, duplicate_of, derived_from, reason, expected_problems
):
    """`find_problems` reports each rule of the statuses that a row breaks, and nothing for a row that breaks none."""
    # --- arrange ----------------------
    final_status_cls = script_modules["data_files"].FinalStatus
    final_statuses = {
        "s:1": final_status_cls("new", "", "", ""),
        "s:2": final_status_cls("incomplete", "", "", "no interval"),
        "s:3": final_status_cls(status, duplicate_of, derived_from, reason),
        "s:4": final_status_cls("new", "", "", ""),
    }

    # --- act --------------------------
    problems = script_modules["statuses"].find_problems(final_statuses, decisions={})

    # --- assert -----------------------
    assert problems == expected_problems


# ==================================================================================================
#  The rules of the formulas
# ==================================================================================================
def test_formulas_table_numbers_sources_and_formulas(script_modules):
    """Sources with a `new` row are numbered per subcategory in time order, and their formulas in row order.

    A formula of several rows is numbered at the position of its first row.
    """
    # --- arrange ----------------------
    data_files = script_modules["data_files"]
    lines = [
        ("a:1", "1.1", "new"),
        ("a:2", "1.1", "duplicate"),
        ("a:3", "1.1", "new"),
        ("b:1", "1.1", "incomplete"),  # b has no new row, so it gets no number
        ("c:1", "1.2", "new"),
        ("d:1", "1.1", "new"),
        ("d:2", "1.1", "new"),
        ("d:3", "1.1", "new"),
    ]
    rows = [
        data_files.RowsTableLine(
            row_id,
            2000,
            subcategory,
            "x",
            "",
            "",
            "[0, 1]",
            data_files.AutomaticStatus(status, "", "", "", 1),
            data_files.FinalStatus(status, "", "", ""),
        )
        for row_id, subcategory, status in lines
    ]
    formula_decisions = [data_files.FormulaDecision(("d:3", "d:1"), "", "the same function on another interval")]

    # --- act --------------------------
    formulas_table = script_modules["formulas"].FormulasTable.build(rows, formula_decisions)

    # --- assert -----------------------
    assert [(formula.formula_id, formula.row_ids) for formula in formulas_table.formulas] == [
        ("f1.1.1.1", ("a:1",)),
        ("f1.1.1.2", ("a:3",)),
        ("f1.1.2.1", ("d:1", "d:3")),
        ("f1.1.2.2", ("d:2",)),
        ("f1.2.1.1", ("c:1",)),
    ]


@pytest.mark.parametrize(
    "row_ids, expected_problems",
    [
        (("s:1", "s:3"), []),
        (("s:1", "s:2"), ["formula_decisions.csv names a row that is not new, s:2"]),
        (("s:1", "s:9"), ["formula_decisions.csv names an unknown row, s:9"]),
        (("s:1", "t:1"), ["formula_decisions.csv joins rows of 2 sources, s:1"]),
    ],
)
def test_formula_decision_find_problems(script_modules, row_ids, expected_problems):
    """`FormulaDecision.find_problems` reports each row that a formula may not hold, and nothing for allowed rows."""
    # --- arrange ----------------------
    formula_decision = script_modules["data_files"].FormulaDecision(
        row_ids, "", "the same function on another interval"
    )
    status_by_row_id = {"s:1": "new", "s:2": "duplicate", "s:3": "new", "t:1": "new"}

    # --- act --------------------------
    problems = formula_decision.find_problems(status_by_row_id)

    # --- assert -----------------------
    assert problems == expected_problems
