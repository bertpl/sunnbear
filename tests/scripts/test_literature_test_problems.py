"""The generated files of `data/literature_test_problems/` agree with the folder's source files and decisions.

The tests use the script's modules that need only the standard library; the row comparison in `matching`, which
needs sympy, is not run here, because another sympy version could change a match.
"""

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
        for name in ("data_files", "statuses", "overview")
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


def test_readme_lists_every_decision_column(script_modules, folder):
    """The README's list of the columns of `decisions.csv` equals the columns that the script reads."""
    # --- arrange / act ----------------
    readme = folder.readme_file.read_text(encoding="utf-8")
    columns_sentence = re.search(r"with the columns (.+?)\. ", readme).group(1)
    listed = re.findall(r"`(\w+)`", columns_sentence)

    # --- assert -----------------------
    assert listed == script_modules["data_files"].DECISION_COLUMNS


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
