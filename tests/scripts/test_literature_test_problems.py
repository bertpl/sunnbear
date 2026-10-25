"""The generated files of `data/literature_test_problems/` agree with the folder's source files and decisions.

The tests do not run the row comparison in `matching`, because another sympy version could change a match, and they
do not regenerate the formula modules of category 1 in sunnbear's catalog; they recompute each module's hash from the
survey.
"""

import ast
import inspect
import math
import re
import sys
import textwrap

import pytest

from sunnbear._core.problems.catalog.c01_published_test_problems import PublishedTestProblems
from sunnbear._core.problems.core import FormulaRegistry, FormulaSource

_CATEGORY_1_FORMULAS = [formula for formula in FormulaRegistry.formulas() if formula.number[0] == 1]
# _FIRST_RUN_LINES are the rows of a small survey on its first run, each as (row id, subcategory, final status).
_FIRST_RUN_LINES = [
    ("a:1", "1.1", "new"),
    ("a:2", "1.1", "duplicate"),
    ("a:3", "1.1", "new"),
    ("b:1", "1.1", "incomplete"),  # b has no new row, so it gets no number
    ("c:1", "1.2", "new"),
    ("d:1", "1.1", "new"),
    ("d:2", "1.1", "new"),
    ("d:3", "1.1", "new"),
]


# ==================================================================================================
#  Fixtures
# ==================================================================================================
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
def committed_formulas_table(script_modules, folder):
    """Return the formulas of the committed `formulas.csv`."""
    return script_modules["formulas"].FormulasTable.read(folder.formulas_file)


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


def test_formulas_file_matches_its_inputs(script_modules, folder, rows, formula_decisions, committed_formulas_table):
    """`formulas.csv` equals what the script builds from `rows.csv`, `formula_decisions.csv` and its own ids."""
    # --- arrange / act ----------------
    formulas_table_cls = script_modules["formulas"].FormulasTable
    built = formulas_table_cls.build(rows, formula_decisions, committed_formulas_table).csv_text()

    # --- assert -----------------------
    assert built == folder.formulas_file.read_text(encoding="utf-8")


def test_formulas_file_holds_every_new_row_once(rows, committed_formulas_table):
    """The active formulas of `formulas.csv` name every `new` row exactly once, and no other row."""
    # --- arrange / act ----------------
    named_row_ids = [
        row_id for formula in committed_formulas_table.formulas if not formula.is_retired for row_id in formula.row_ids
    ]
    new_row_ids = [row.row_id for row in rows if row.final_status.status == "new"]

    # --- assert -----------------------
    assert sorted(named_row_ids) == sorted(new_row_ids)


def test_formulas_file_keeps_each_formula_within_its_source(script_modules, committed_formulas_table):
    """Every row of a formula in `formulas.csv` comes from the formula's own source."""
    # --- arrange / act ----------------
    rows_of_other_sources = [
        (formula.formula_id, row_id)
        for formula in committed_formulas_table.formulas
        for row_id in formula.row_ids
        if script_modules["data_files"].source_id_of_row_id(row_id) != formula.source_id
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


def test_readme_lists_every_file(script_modules, folder):
    """The README's table of files names every file of `DataFolder` except the README itself."""
    # --- arrange / act ----------------
    readme = folder.readme_file.read_text(encoding="utf-8")
    files_section = readme.split("\n## Files\n")[1].split("\n## ")[0]
    listed = set(re.findall(r"^\| `([^`/]+)` \|", files_section, re.MULTILINE))
    property_names = [name for name in vars(script_modules["data_files"].DataFolder) if name.endswith("_file")]
    file_names = {getattr(folder, name).name for name in property_names} - {folder.readme_file.name}

    # --- assert -----------------------
    assert listed == file_names


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
#  The formulas of category 1 in sunnbear's catalog
# ==================================================================================================
@pytest.mark.parametrize("formula", _CATEGORY_1_FORMULAS, ids=lambda formula: formula.label)
def test_category_1_formula_matches_the_survey(formula, script_modules, sources, committed_formulas_table):
    """A formula of category 1 has an active line in `formulas.csv`, and its category and `source` match its source.

    The category's name must be the source's short title, and `source` must hold the source's reference and its rows'
    keys as the location.

    A generated module's hash must equal the hash of its survey fields, so that a module left stale after a change
    of the survey fails; a module has no hash exactly when it is hand-written: when a row of its formula only
    describes its function, or the formula is 1 of the generator's `UNTRANSLATABLE_FORMULAS` or `MODIFIED_FORMULAS`.
    """
    # --- arrange ----------------------
    line = {line.number: line for line in committed_formulas_table.formulas}[formula.number]
    source = {source.source_id: source for source in sources}[line.source_id]
    survey_formula = script_modules["formulas"].SurveyFormula(line, source)
    category = {category.number: category for category in FormulaRegistry.categories()}[formula.number[:3]]
    survey_fields_hash = getattr(sys.modules[type(formula).__module__], "SURVEY_FIELDS_HASH", None)

    # --- act --------------------------
    location = ", ".join(source.find_row(row_id).key for row_id in line.row_ids)

    # --- assert -----------------------
    assert not line.is_retired
    assert category.name == source.short_title
    assert formula.source == FormulaSource(reference=source.reference, location=location)
    if script_modules["formula_modules"].is_hand_written(survey_formula):
        assert survey_fields_hash is None
    else:
        assert survey_fields_hash == script_modules["formula_modules"].FormulaModuleSpec.survey_fields_hash(
            survey_formula
        )


def test_category_1_sources_in_the_catalog_are_complete(committed_formulas_table):
    """A source with a formula in the catalog has each of its active formulas of `formulas.csv` there."""
    # --- arrange ----------------------
    numbers_in_catalog = {formula.number for formula in _CATEGORY_1_FORMULAS}
    source_numbers_in_catalog = {number[:3] for number in numbers_in_catalog}

    # --- act --------------------------
    missing = [
        line.formula_id
        for line in committed_formulas_table.formulas
        if not line.is_retired
        and line.source_number in source_numbers_in_catalog
        and line.number not in numbers_in_catalog
    ]

    # --- assert -----------------------
    assert numbers_in_catalog
    assert missing == []


def test_modified_formulas_are_the_formulas_with_the_parameter_modified(script_modules):
    """`MODIFIED_FORMULAS` lists exactly the formulas of category 1 that have the parameter ``modified``."""
    # --- act --------------------------
    formula_ids_with_parameter_modified = {
        f"f{formula.format_number(formula.number)}"
        for formula in _CATEGORY_1_FORMULAS
        if "modified" in formula.param_names
    }

    # --- assert -----------------------
    assert formula_ids_with_parameter_modified == set(script_modules["modified_formulas"].MODIFIED_FORMULAS)


@pytest.mark.parametrize("formula", _CATEGORY_1_FORMULAS, ids=lambda formula: formula.label)
@pytest.mark.parametrize("c", [0.25, -0.25])
def test_category_1_formula_applies_c_as_its_rule_says(formula, c, script_modules):
    """A formula of category 1 applies ``c`` by category 1's rule, or by its `ModificationType` where ``modified = 1``.

    The expected value evaluates the formula at ``c = 0``, which repeats the formula's own float arithmetic, so the
    value at ``c`` equals the expected value exactly. The equality holds:

    - for a shift along x, because the test subtracts ``c_scale*c`` from x as the formula does;
    - for ``C_ADDS_TO_F``, because such a formula adds ``c`` as its last operation;
    - for ``C_SCALES_X``, because the test scales x with the formula's own operations.
    """
    for candidate in formula.build_all_candidates():
        # --- arrange ----------------------
        modification_type_enum = script_modules["modified_formulas"].ModificationType
        modification_type = _modification_type(candidate, script_modules)
        c_scale = PublishedTestProblems.c_scale(candidate.a, candidate.b)
        # the x-value lies at 0.6 of the interval, in log scale for C_SCALES_X, so that the shifted or scaled x-values
        # stay in the interval
        if modification_type is modification_type_enum.C_SCALES_X:
            x = candidate.a * (candidate.b / candidate.a) ** 0.6
        else:
            x = candidate.a + 0.6 * (candidate.b - candidate.a)

        # --- act --------------------------
        value = candidate.xc_fun(x, c)
        if modification_type is modification_type_enum.C_ADDS_TO_F:
            expected = candidate.xc_fun(x, 0.0) + c
        elif modification_type is modification_type_enum.C_SCALES_X:
            expected = candidate.xc_fun(x * math.exp(-c * math.log(candidate.b / candidate.a)), 0.0)
        else:
            expected = candidate.xc_fun(x - c_scale * c, 0.0)

        # --- assert -----------------------
        assert value == expected, candidate.id


@pytest.mark.parametrize("formula", _CATEGORY_1_FORMULAS, ids=lambda formula: formula.label)
def test_category_1_formula_c_scale_is_its_rounded_interval_width(formula, script_modules):
    """A formula of category 1 multiplies ``c`` by its interval's width, rounded by ``PublishedTestProblems.c_scale``.

    The test reads the factor from the code of ``parametrized_fun``, because a test that compares shifted values
    cannot see a number that is 1 float step off, such as ``1.9999999999999996`` for ``2.0``: the shifted x-values
    round to the same float.

    The test skips a test problem with ``modified = 1`` whose ``ModificationType.is_x_shifted_by_c_scale`` is false,
    because such a test problem applies ``c`` with no factor ``c_scale``.
    """
    # --- arrange ----------------------
    tree = ast.parse(textwrap.dedent(inspect.getsource(type(formula).parametrized_fun)))
    shifting_candidates = []
    for candidate in formula.build_all_candidates():
        modification_type = _modification_type(candidate, script_modules)
        if modification_type is None or modification_type.is_x_shifted_by_c_scale:
            shifting_candidates.append(candidate)

    # --- act --------------------------
    factors = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Mult)
            and isinstance(node.right, ast.Name)
            and node.right.id == "c"
        ):
            factors.append(node.left)

    # --- assert -----------------------
    assert len(factors) == 1
    for candidate in shifting_candidates:
        c_scale = PublishedTestProblems.c_scale(candidate.a, candidate.b)
        if isinstance(factors[0], ast.Name):
            params = dict(zip(candidate.id.param_names, candidate.id.param_values, strict=True))
            assert factors[0].id == "c_scale"
            assert params["c_scale"] == c_scale, candidate.id
        else:
            assert ast.literal_eval(factors[0]) == c_scale, candidate.id


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
    """From an empty committed table, sources are numbered per subcategory in time order, formulas by first row."""
    # --- arrange ----------------------
    rows = _rows_table_lines(script_modules, _FIRST_RUN_LINES)
    formula_decisions = _formula_decisions(script_modules, [("d:3", "d:1")])
    formulas_table_cls = script_modules["formulas"].FormulasTable

    # --- act --------------------------
    formulas_table = formulas_table_cls.build(rows, formula_decisions, formulas_table_cls(()))

    # --- assert -----------------------
    assert [(formula.formula_id, formula.row_ids) for formula in formulas_table.formulas] == [
        ("f1.1.1.1", ("a:1",)),
        ("f1.1.1.2", ("a:3",)),
        ("f1.1.2.1", ("d:1", "d:3")),
        ("f1.1.2.2", ("d:2",)),
        ("f1.2.1.1", ("c:1",)),
    ]


def test_formulas_table_appends_new_ids_and_retires_old_ones(script_modules):
    """A changed survey keeps every committed id, appends new ids, and retires a formula whose row is not `new`."""
    # --- arrange ----------------------
    formula_decisions = _formula_decisions(script_modules, [("d:3", "d:1")])
    first_run_formulas_table = _first_run_formulas_table(script_modules)
    later_lines = [
        ("z:1", "1.1", "new"),  # z is an older source that was added later
        ("a:1", "1.1", "new"),
        ("a:4", "1.1", "new"),  # a:4 is a row that was added between a's rows
        ("a:2", "1.1", "duplicate"),
        ("a:3", "1.1", "duplicate"),  # a:3 is now a duplicate of z:1
        ("b:1", "1.1", "new"),  # b's row became complete, so b gets a number
        ("c:1", "1.2", "new"),
        ("d:1", "1.1", "new"),
        ("d:2", "1.1", "new"),
        ("d:3", "1.1", "new"),
    ]

    # --- act --------------------------
    formulas_table = script_modules["formulas"].FormulasTable.build(
        _rows_table_lines(script_modules, later_lines), formula_decisions, first_run_formulas_table
    )

    # --- assert -----------------------
    assert [(formula.formula_id, formula.row_ids, formula.is_retired) for formula in formulas_table.formulas] == [
        ("f1.1.1.1", ("a:1",), False),
        ("f1.1.1.2", ("a:3",), True),
        ("f1.1.1.3", ("a:4",), False),
        ("f1.1.2.1", ("d:1", "d:3"), False),
        ("f1.1.2.2", ("d:2",), False),
        ("f1.1.3.1", ("z:1",), False),
        ("f1.1.4.1", ("b:1",), False),
        ("f1.2.1.1", ("c:1",), False),
    ]


def test_formulas_table_reactivates_a_retired_formula(script_modules):
    """A retired formula whose rows are `new` again becomes active again with its own id."""
    # --- arrange ----------------------
    formulas_table_cls = script_modules["formulas"].FormulasTable
    formula_decisions = _formula_decisions(script_modules, [("d:3", "d:1")])
    first_run_formulas_table = _first_run_formulas_table(script_modules)
    a3_duplicate_lines = [
        (row_id, subcategory, "duplicate" if row_id == "a:3" else status)
        for row_id, subcategory, status in _FIRST_RUN_LINES
    ]
    a3_retired_formulas_table = formulas_table_cls.build(
        _rows_table_lines(script_modules, a3_duplicate_lines), formula_decisions, first_run_formulas_table
    )

    # --- act --------------------------
    formulas_table = formulas_table_cls.build(
        _rows_table_lines(script_modules, _FIRST_RUN_LINES), formula_decisions, a3_retired_formulas_table
    )

    # --- assert -----------------------
    assert formulas_table == first_run_formulas_table


@pytest.mark.parametrize(
    "lines, decided_row_id_groups, expected_problems",
    [
        # A decision joins 2 committed formulas.
        (_FIRST_RUN_LINES, [("d:1", "d:2", "d:3")], ["the formula of d:1 would join f1.1.2.1, f1.1.2.2"]),
        # A removed decision splits a committed formula.
        (
            _FIRST_RUN_LINES,
            [],
            ["the formula of d:1 would split from f1.1.2.1", "the formula of d:3 would split from f1.1.2.1"],
        ),
        # A row no longer exists.
        (
            [line for line in _FIRST_RUN_LINES if line[0] != "d:2"],
            [("d:3", "d:1")],
            ["f1.1.2.2 names a row that no longer exists, d:2"],
        ),
        # A source moved to another subcategory.
        (
            [
                (row_id, "1.1" if row_id == "c:1" else subcategory, status)
                for row_id, subcategory, status in _FIRST_RUN_LINES
            ],
            [("d:3", "d:1")],
            ["the source of f1.2.1.1 is now in another subcategory"],
        ),
    ],
)
def test_formulas_table_stops_on_a_change_of_an_id(script_modules, lines, decided_row_id_groups, expected_problems):
    """`FormulasTable.build` raises `FormulaIdChangeError` with every change that would change a committed id."""
    # --- arrange ----------------------
    formulas_module = script_modules["formulas"]
    first_run_formulas_table = _first_run_formulas_table(script_modules)

    # --- act --------------------------
    with pytest.raises(formulas_module.FormulaIdChangeError) as error:
        formulas_module.FormulasTable.build(
            _rows_table_lines(script_modules, lines),
            _formula_decisions(script_modules, decided_row_id_groups),
            first_run_formulas_table,
        )

    # --- assert -----------------------
    assert error.value.problems == expected_problems


@pytest.mark.parametrize(
    "later_lines, decided_row_id_groups, expected_formulas",
    [
        # A row of d's 2-row formula is a duplicate now: the formula keeps its id with 1 row.
        (
            [
                (row_id, subcategory, "duplicate" if row_id == "d:3" else status)
                for row_id, subcategory, status in _FIRST_RUN_LINES
            ],
            [("d:3", "d:1")],
            [("f1.1.2.1", ("d:1",), False), ("f1.1.2.2", ("d:2",), False)],
        ),
        # A row that became `new` joins d's formula through a decision: the formula keeps its id with 3 rows.
        (
            [*_FIRST_RUN_LINES, ("d:4", "1.1", "new")],
            [("d:3", "d:1", "d:4")],
            [("f1.1.2.1", ("d:1", "d:3", "d:4"), False), ("f1.1.2.2", ("d:2",), False)],
        ),
    ],
)
def test_formulas_table_keeps_the_id_of_a_formula_whose_rows_change(
    script_modules, later_lines, decided_row_id_groups, expected_formulas
):
    """A formula whose rows shrink or grow, without joining another formula, keeps its id."""
    # --- arrange ----------------------
    first_run_formulas_table = _first_run_formulas_table(script_modules)

    # --- act --------------------------
    formulas_table = script_modules["formulas"].FormulasTable.build(
        _rows_table_lines(script_modules, later_lines),
        _formula_decisions(script_modules, decided_row_id_groups),
        first_run_formulas_table,
    )

    # --- assert -----------------------
    d_formulas = [
        (formula.formula_id, formula.row_ids, formula.is_retired)
        for formula in formulas_table.formulas
        if formula.source_id == "d"
    ]
    assert d_formulas == expected_formulas


def test_formulas_table_keeps_a_retired_id_that_a_person_resolved(script_modules):
    """A retired line keeps its id from being given again, also when another formula holds its rows or they are gone."""
    # --- arrange ----------------------
    formulas_module = script_modules["formulas"]
    formulas_table_line_cls = formulas_module.FormulasTableLine
    no_function_decision = script_modules["data_files"].FunctionDecision()
    # a person resolved the join of f1.1.2.1 and f1.1.2.2: f1.1.2.1 holds d:1, d:2 and d:3, f1.1.2.2 is retired, and
    # the formula of a removed row x:1 was retired too
    resolved_table = formulas_module.FormulasTable(
        (
            formulas_table_line_cls((1, 1, 1, 1), "a", ("a:1",), no_function_decision, is_retired=False),
            formulas_table_line_cls((1, 1, 1, 2), "a", ("a:3",), no_function_decision, is_retired=False),
            formulas_table_line_cls((1, 1, 1, 3), "a", ("a:9",), no_function_decision, is_retired=True),
            formulas_table_line_cls((1, 1, 2, 1), "d", ("d:1", "d:2", "d:3"), no_function_decision, is_retired=False),
            formulas_table_line_cls((1, 1, 2, 2), "d", ("d:2",), no_function_decision, is_retired=True),
            formulas_table_line_cls((1, 2, 1, 1), "c", ("c:1",), no_function_decision, is_retired=False),
        )
    )
    later_lines = [*_FIRST_RUN_LINES, ("a:4", "1.1", "new"), ("d:4", "1.1", "new")]

    # --- act --------------------------
    formulas_table = formulas_module.FormulasTable.build(
        _rows_table_lines(script_modules, later_lines),
        _formula_decisions(script_modules, [("d:1", "d:2", "d:3")]),
        resolved_table,
    )

    # --- assert -----------------------
    appended = [formula for formula in formulas_table.formulas if formula not in resolved_table.formulas]
    assert [(formula.formula_id, formula.row_ids) for formula in appended] == [
        ("f1.1.1.4", ("a:4",)),
        ("f1.1.2.3", ("d:4",)),
    ]


@pytest.mark.parametrize(
    "lines, expected_message",
    [
        (["f1.1.1.1,active,zz,a:1,,,"], "a formula names a row of another source than its source_id"),
        (["f1.1.1.1,active,a"], "the line of f1.1.1.1 does not have 7 fields"),
        (["f1.1.1.1,active,a,a:1,,,", "f1.1.1.2,active,a,a:1,,,"], "a row is in more than 1 active formula"),
        (["f1.1.1.1,active,a,a:1,,,", "f1.1.1.1,retired,a,a:2,,,"], "an id is in more than 1 line"),
        (["f1.1.1.1,active,a,a:1,,,", "f1.1.1.2,active,b,b:1,,,"], "a source number belongs to more than 1 source"),
        (["f1.1.1.1,active,a,a:1,,,", "f1.1.2.1,active,a,a:2,,,"], "a source has more than 1 number in 1 subcategory"),
        (["g1.1.1.1,active,a,a:1,,,"], "the line of g1.1.1.1 breaks the format"),
    ],
)
def test_formulas_table_read_rejects_a_broken_file(script_modules, tmp_path, lines, expected_message):
    """`FormulasTable.read` raises `DataFileError` for each way that a file, such as one edited by hand, can break."""
    # --- arrange ----------------------
    path = tmp_path / "formulas.csv"
    path.write_text("\n".join(["formula_id,status,source_id,row_ids,variable_change,f,parameters", *lines]) + "\n")

    # --- act / assert -----------------
    with pytest.raises(script_modules["data_files"].DataFileError, match=re.escape(expected_message)):
        script_modules["formulas"].FormulasTable.read(path)


def test_source_with_a_repeated_key_is_rejected(script_modules, tmp_path):
    """A source file that gives 2 rows the same key raises `DataFileError`, so that no row id depends on position."""
    # --- arrange ----------------------
    path = tmp_path / "2000_a.toml"
    path.write_text(
        """title = 'A (2000): a'
reference = 'A (2000).'
year = 2000
subcategory = '1.1'
where_in_source = 'Table 1'
transcribed_from = 'the article'
rows_summary = '2 rows'

[[rows]]
key = '3'
f = 'sin(x)'

[[rows]]
key = '3'
f = 'cos(x)'
"""
    )

    # --- act / assert -----------------
    with pytest.raises(script_modules["data_files"].DataFileError, match="is in more than 1 row"):
        script_modules["data_files"].Source.from_toml_file(path)


def test_formulas_table_read_of_a_missing_file_is_empty(script_modules, tmp_path):
    """Without `formulas.csv`, `FormulasTable.read` returns an empty table."""
    # --- arrange / act ----------------
    formulas_table = script_modules["formulas"].FormulasTable.read(tmp_path / "formulas.csv")

    # --- assert -----------------------
    assert formulas_table.formulas == ()


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
    data_files = script_modules["data_files"]
    formula_decision = data_files.FormulaDecision(
        row_ids, data_files.FunctionDecision(), "the same function on another interval"
    )
    status_by_row_id = {"s:1": "new", "s:2": "duplicate", "s:3": "new", "t:1": "new"}

    # --- act --------------------------
    problems = formula_decision.find_problems(status_by_row_id)

    # --- assert -----------------------
    assert problems == expected_problems


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _rows_table_lines(script_modules, lines):
    """Return a row of `rows.csv` for each (row id, subcategory, final status) of `lines`, in the same order."""
    data_files = script_modules["data_files"]
    return [
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


def _formula_decisions(script_modules, decided_row_id_groups):
    """Return a formula decision for each tuple of row ids of `decided_row_id_groups`."""
    data_files = script_modules["data_files"]
    return [
        data_files.FormulaDecision(row_ids, data_files.FunctionDecision(), "the same function on another interval")
        for row_ids in decided_row_id_groups
    ]


def _first_run_formulas_table(script_modules):
    """Return the formulas that `_FIRST_RUN_LINES` give from an empty committed table, with d:1 and d:3 in 1 formula."""
    formulas_table_cls = script_modules["formulas"].FormulasTable
    return formulas_table_cls.build(
        _rows_table_lines(script_modules, _FIRST_RUN_LINES),
        _formula_decisions(script_modules, [("d:3", "d:1")]),
        formulas_table_cls(()),
    )


def _modification_type(candidate, script_modules):
    """Return the `ModificationType` of a test problem with ``modified = 1``, and None for a published one."""
    params = dict(zip(candidate.id.param_names, candidate.id.param_values, strict=True))
    if params.get("modified") == 1.0:
        return script_modules["modified_formulas"].MODIFIED_FORMULAS[candidate.id.formula_id]
    else:
        return None
