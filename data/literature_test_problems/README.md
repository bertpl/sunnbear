# Literature test problems

**Nothing in this folder ships with the sunnbear package.** The data artifacts that ship are those of `sunnbear.data`; this folder is maintainer data, read only by the script `scripts/literature_test_problems/` and its test.

The folder is a survey of the test functions that published sources give: articles of root-finding methods, public benchmark suites and textbooks. Each row is 1 test function as its source gives it, with its parameters and interval, and each row records whether an earlier source already gives the same function. The rows are the material for the formulas of category 1 of sunnbear's formula catalog, *Existing benchmark suites*.

## Files

| file | written by | content |
|---|---|---|
| `sources/<id>.toml` | hand | 1 source: its reference, where in the source its rows are, and its rows |
| `decisions.csv` | hand | the statuses that a person decided, where the script cannot decide or decides wrongly |
| `rows.csv` | script | every row, in time order, with its automatic and its final status |
| `summary.md` | script | 1 line per source: its year, title, home, rows and new rows, and the sources that it takes rows from |
| `timeline.html` | script | a page that draws the sources in time order, with an edge from each source to the later sources that take its rows |

Do not edit the 3 generated files by hand; regenerate them (§ Regenerating).

## Source files

A source's id is its file name: `<year>_<first author>_<subject>` for a publication, such as `1971_dowell_jarratt_illinois`, and the suite's name for a code suite, such as `roots_fortran`. Each file holds these fields:

| field | content |
|---|---|
| `title` | `Authors (year): subject`; the page shows the part before the colon |
| `reference` | the full reference with its DOI, or its URL where it has none |
| `year` | the year of the edition or version that the rows come from, below |
| `home` | the subcategory of category 1 where the source's formulas belong, below |
| `where_in_source` | the tables, sections or files of the source that hold the functions |
| `transcribed_from` | what the rows were read from, and which one wins where they differ |
| `rows_summary` | the number of rows, first, and how they relate to the source's own count |
| `notes` | optional: how to read the rows of this source, and other facts about it |
| `[[relations]]` | optional, any number: `sources`, the ids of other sources, and `text`, how this source's rows relate to theirs |
| `[[rows]]` | 1 table per row, below |

**Year.** A textbook's year is that of the edition that the rows come from, and a code suite's that of its release or commit. An article that appeared online before its issue takes the online year, so the year can differ from the one in its id (`2021_oliveira_takahashi` appeared online in 2020). The sources are in time order by year, then by id without its leading year.

**Home**, the kind of source:

- `1.1`: articles of solvers that sunnbear implements
- `1.2`: articles of other solvers
- `1.3`: public benchmark suites
- `1.4`: textbooks

**A row** has these fields; only `key` and 1 of `f` and `f_description` are required:

| field | content |
|---|---|
| `key` | the source's own label for the function (`15`, `f34`, `2.4`), or a label from its section and position if it has none |
| `name` | the source's name for the function |
| `f` | the function as 1 expression in ASCII operators (`x^n - 0.2`, `exp(-n*x)`, `sqrt(x)`), or an equation `lhs = rhs` |
| `f_description` | instead of `f`: a function that 1 expression does not give, such as a piecewise function or one that needs data |
| `parameters` | the values of the source's own parameters, as published (`n = 4, 6, 8, 10, 12`) |
| `interval` | the interval or intervals as published, or the starting points where the source gives no interval |
| `also_in` | other sources of the function, where this source names them |
| `notes` | what a reader needs to read the row, such as a rounded constant or a misprint |

A row's id is `<source id>:<key>`, such as `2011_zhang:3`; a key that a source repeats gets `#2`, `#3`, ... in the order of the rows. Every text field is markdown, with code in backticks; a field that holds only code, such as `interval = '[0, 1]'`, is written without them.

## Statuses

Each row has 1 of 4 final statuses; every status other than `new` names the earlier row or rows that the row matches, the earliest one that does:

- **`duplicate`:** the same expression written differently without changing how it is computed (reordered terms or factors, `x*x*x` against `x^3`), the same expression on another interval, a sign flip, a constant factor, or an equation against its difference form (`sin(x) = x^2` against `sin(x) - x^2`).
- **`variant`:** the same model with other constants (`g = 9.8` against `9.81`), or a shift in `x`.
- **`extended`:** a family that only adds parameter values to an earlier family.
- **`new`:** everything else. That includes a function with the same roots but other values, such as 2 fixed-point forms `x = g(x)` of 1 equation, and the same function in a form that rounds differently, such as a polynomial in expanded against factored or nested form.

Where a source misprints a function, the row is compared as the function that the source meant, and its notes say so. The rules guarantee one thing: every row that is not `new` names an earlier row. A duplicate that they miss stays `new`.

**How the script decides.** It parses each row's `f` and `parameters` with sympy into 1 instance per combination of parameter values, and compares each row with every earlier row (the docstring of `scripts/literature_test_problems/matching.py` gives the 3 comparisons). A row whose every instance an earlier row already has is a `duplicate`; a row whose expression matches an earlier family, with new parameter values, is `extended`; a row that parses and matches nothing is `new`. Every other row gets the status `judge`, which a person decides in `decisions.csv`: a match by value only, a partial match, or a row that does not parse. A row that does not parse still matches an earlier row with the same text.

**Chains end at the first appearance:** a row whose earlier row is itself a `duplicate` names that row's earlier row instead. A `variant` or `extended` row stays named, since it is the first appearance of its constants or parameter values.

## Decisions

`decisions.csv` holds 1 line per row that a person decided, with the columns `row_id`, `status`, `earlier_rows` and `reason`. A decision wins over the script's automatic status, so it also corrects a wrong one. `earlier_rows` separates several row ids by ` | `.

## The table of rows

`rows.csv` repeats each row's `f`, `f_description`, `parameters` and `interval`, and adds:

| column | content |
|---|---|
| `row_id`, `year`, `home` | the row's id, and its source's year and home |
| `parse_note` | why the script could not parse the row; empty when it parsed |
| `instances` | the number of the row's parsed instances |
| `auto_status`, `match_kind`, `matches` | the script's status, the comparison that found it, and the earlier rows that matched |
| `status`, `earlier_rows`, `reason` | the final status, from `decisions.csv` where it decides the row |

## The summary and the page

An edge runs from an earlier source to a later one for every later row that names a row of the earlier source; `summary.md` lists the edges into each source as *takes rows from*. Short functions that many sources hold, such as `cos(x) - x`, would join nearly every source, so they give no edges: a row is such a common function when later rows of at least `COMMON_SOURCES` sources name it and its `f` is at most `COMMON_MAX_LENGTH` characters long (both set in `scripts/literature_test_problems/overview.py`). Common functions still count in the rows of their sources, and `summary.md` lists them.

## Adding a source

1. Write `sources/<id>.toml`, and add a relation for every source that it takes rows from or that takes rows from it.
2. Regenerate. The script prints each row that needs a decision; `rows.csv` gives the comparison and the earlier rows that the script found for it.
3. Add a line to `decisions.csv` for each of those rows, and for any automatic status that is wrong, then regenerate until the script prints no problems.
4. Commit the source file, `decisions.csv` and the 3 generated files together.

## Regenerating

From the repo root, with the dev dependencies installed:

```
uv run python -m scripts.literature_test_problems
```

The script writes the 3 generated files, prints the counts per status and every problem that it finds, and exits with status 1 if there is one. It needs sympy, from the dev dependency group, and a Unix system, because it limits the time of each parse with `SIGALRM`.

CI does not regenerate `rows.csv`, because another sympy version could change a match. Instead, `tests/scripts/test_literature_test_problems.py` checks, with the standard library only, that:

- `rows.csv` holds exactly the rows of the source files;
- every decision is applied, and no row names an unknown or a later row;
- every source file has its fields;
- `summary.md` and `timeline.html` equal what the script builds from `rows.csv` and the source files.

A change to the matching in `scripts/literature_test_problems/` is the one change that the test cannot see: whoever makes it regenerates `rows.csv`.
