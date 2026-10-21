"""The generated files of `data/literature_test_problems/` agree with the folder's source files and decisions.

The tests use the script's modules that need only the standard library; the statuses stage, which needs sympy, is
not run here, because another sympy version could change a match.
"""

import importlib
import importlib.util
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
        (row.row_id, source.year, source.home, row.f, row.f_description, row.parameters, row.interval)
        for source in sources
        for row in source.rows
    ]
    from_table = [(r.row_id, r.year, r.home, r.f, r.f_description, r.parameters, r.interval) for r in rows]

    # --- assert -----------------------
    assert from_table == from_sources


def test_rows_table_applies_every_decision(script_modules, rows, decisions):
    """The final statuses in `rows.csv` equal its automatic statuses with every decision applied."""
    # --- arrange ----------------------
    automatic_statuses = {row.row_id: row.automatic for row in rows}

    # --- act --------------------------
    final_statuses = script_modules["statuses"].decide_final_statuses(automatic_statuses, decisions)

    # --- assert -----------------------
    assert {row.row_id: row.final for row in rows} == final_statuses


def test_rows_table_has_no_problems(script_modules, rows, decisions):
    """The final statuses in `rows.csv` have no problems: every row is decided and names only earlier rows."""
    # --- act --------------------------
    problems = script_modules["statuses"].find_problems({row.row_id: row.final for row in rows}, decisions)

    # --- assert -----------------------
    assert problems == []


@pytest.mark.parametrize(
    "file_property, build_method",
    [
        ("summary_file", "summary_markdown"),
        ("timeline_file", "timeline_page"),
    ],
)
def test_overview_file_matches_its_inputs(script_modules, folder, sources, rows, file_property, build_method):
    """Each overview file equals what the script builds from the source files and `rows.csv`."""
    # --- arrange / act ----------------
    overview = script_modules["overview"].Overview.build(sources, rows)
    built = getattr(overview, build_method)()

    # --- assert -----------------------
    assert built == getattr(folder, file_property).read_text(encoding="utf-8")


# ==================================================================================================
#  The rules of the final statuses
# ==================================================================================================
@pytest.mark.parametrize(
    "middle_status, expected_earlier_rows",
    [
        ("duplicate", "s:1"),  # a duplicate of a duplicate names the first appearance
        ("variant", "s:2"),  # a variant is the first appearance of its constants, so it stays named
    ],
)
def test_decide_final_statuses_follows_duplicates_to_the_first_appearance(
    script_modules, middle_status, expected_earlier_rows
):
    """A row that names a duplicate names that duplicate's first appearance; a named variant stays named."""
    # --- arrange ----------------------
    data_files = script_modules["data_files"]
    automatic_statuses = {
        "s:1": data_files.AutomaticStatus("new", "", "", "", 1),
        "s:2": data_files.AutomaticStatus(middle_status, "structure", "s:1", "", 1),
        "s:3": data_files.AutomaticStatus("duplicate", "structure", "s:2", "", 1),
    }

    # --- act --------------------------
    final_statuses = script_modules["statuses"].decide_final_statuses(automatic_statuses, decisions={})

    # --- assert -----------------------
    assert final_statuses["s:3"].earlier_rows == expected_earlier_rows
