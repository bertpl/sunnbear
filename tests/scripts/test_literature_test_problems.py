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
def script() -> dict[str, ModuleType]:
    """Return the script's modules that need only the standard library, imported by path, keyed by name."""
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
def folder(script):
    return script["data_files"].DataFolder.in_repo()


@pytest.fixture(scope="module")
def sources(script, folder):
    return script["data_files"].read_sources(folder.sources_dir)


@pytest.fixture(scope="module")
def rows(script, folder):
    return script["data_files"].read_rows_table(folder.rows_file)


@pytest.fixture(scope="module")
def decisions(script, folder):
    return script["data_files"].read_decisions(folder.decisions_file)


# ==================================================================================================
#  The committed files
# ==================================================================================================
def test_rows_table_holds_the_rows_of_the_source_files(sources, rows):
    # --- arrange / act ----------------
    from_sources = [
        (row.row_id, source.year, source.home, row.f, row.f_description, row.parameters, row.interval)
        for source in sources
        for row in source.rows
    ]
    from_table = [(r.row_id, r.year, r.home, r.f, r.f_description, r.parameters, r.interval) for r in rows]

    # --- assert -----------------------
    assert from_table == from_sources


def test_rows_table_applies_every_decision(script, rows, decisions):
    # --- arrange ----------------------
    automatic = {row.row_id: row.automatic for row in rows}

    # --- act --------------------------
    final = script["statuses"].decide_final_statuses(automatic, decisions)

    # --- assert -----------------------
    assert {row.row_id: row.final for row in rows} == final


def test_rows_table_has_no_problems(script, rows, decisions):
    # --- act --------------------------
    problems = script["statuses"].find_problems({row.row_id: row.final for row in rows}, decisions)

    # --- assert -----------------------
    assert problems == []


@pytest.mark.parametrize(
    "file_property, build_method",
    [
        ("summary_file", "summary_markdown"),
        ("timeline_file", "timeline_page"),
    ],
)
def test_overview_file_matches_its_inputs(script, folder, sources, rows, file_property, build_method):
    # --- arrange / act ----------------
    overview = script["overview"].Overview.build(sources, rows)
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
def test_decide_final_statuses_follows_duplicates_to_the_first_appearance(script, middle_status, expected_earlier_rows):
    # --- arrange ----------------------
    data_files = script["data_files"]
    automatic = {
        "s:1": data_files.AutomaticStatus("new", "", "", "", 1),
        "s:2": data_files.AutomaticStatus(middle_status, "structure", "s:1", "", 1),
        "s:3": data_files.AutomaticStatus("duplicate", "structure", "s:2", "", 1),
    }

    # --- act --------------------------
    final = script["statuses"].decide_final_statuses(automatic, decisions={})

    # --- assert -----------------------
    assert final["s:3"].earlier_rows == expected_earlier_rows
