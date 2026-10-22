# Literature test problems

**Nothing in this folder ships with the sunnbear package.** The data artifacts that ship are those of `sunnbear.data`; this folder is maintainer data, read only by the script `scripts/literature_test_problems/` and its test.

The folder is a survey of the test functions of published sources: articles of root-finding methods, public benchmark suites and textbooks.

Each row is 1 function as its source gives it, with its parameters and intervals. A row's test functions are its function at each combination of its parameter values, on each of its intervals.

A row's status records whether the source gives enough to define those test functions, and whether an earlier source already gives them all.

The rows are the material for category 1, *Published test functions*, of sunnbear's formula catalog. The catalog holds the package's formulas in `sunnbear.functions`, each a family of test functions.

## Files

| file | written by | content |
|---|---|---|
| `sources/<id>.toml` | hand | 1 source: its reference, where in the source its rows are, and its rows |
| `decisions.csv` | hand | the statuses that a person decided, where the script cannot decide or decides wrongly (§ Decisions) |
| `formula_decisions.csv` | hand | the formulas that hold several rows, or whose variable differs from the variable of their row's function (§ Formulas) |
| `rows.csv` | script | every row, in time order, with its automatic and its final status (§ Statuses) |
| `summary.md` | script | 1 line per source: its year, title, subcategory (the kind of source, § Source files), rows and new rows, and the sources that it takes rows from |
| `timeline.html` | script | a page that draws the sources in time order, with an edge from each source to every later source whose rows name its rows (§ The summary and the page) |
| `formulas.csv` | script | every formula of category 1, active and retired, with its rows; the script keeps every id that the file already holds (§ Formulas) |

Do not edit the generated files by hand; regenerate them (§ Regenerating). The 1 exception is `formulas.csv` after the script stops on a change that would change the id of a formula: a person then edits `formulas.csv` by hand (§ Formulas).

## Source files

A source's id is its file name: `<year>_<author names>` for a publication, optionally followed by `_<subject>`, such as `2011_zhang` and `1971_dowell_jarratt_illinois`, and the suite's name for a code suite, such as `roots_fortran`. Each file holds these fields:

| field | content |
|---|---|
| `title` | `Authors (year): subject`; `timeline.html` shows the part before the colon |
| `reference` | the full reference with its DOI, or its URL where it has none |
| `year` | the year of the edition or version that `reference` cites (see **Year** below) |
| `subcategory` | the subcategory of category 1 where the source's formulas belong (see **Subcategory** below) |
| `where_in_source` | the tables, sections or files of the source that hold the functions |
| `transcribed_from` | what the rows were read from, and which one is followed where they differ |
| `rows_summary` | starts with the number of rows, then says how that number relates to the source's own count |
| `notes` | optional: how to read the rows of this source, and other facts about it |
| `[[relations]]` | optional, any number: `sources`, the ids of other sources, and `text`, how this source's rows relate to theirs |
| `[[rows]]` | 1 table per row, below |

**Year.** A textbook's year is that of the cited edition, and a code suite's that of the cited release or commit. An article that appeared online before its issue takes the online year, so the year can differ from the one in its id (`2021_oliveira_takahashi` appeared online in 2020).

The generated files list the sources in time order: by year, then by id without its leading year.

**Subcategory** gives the kind of source:

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
| `interval` | the interval or intervals as published, including the x-range of a figure that plots the function where both bounds can be read exactly, such as `` `[0, 2]` (Fig. 2.2) ``; or the starting points where the source gives no interval |
| `also_in` | other sources of the function, where this source names them |
| `notes` | what a reader needs to read the row, such as a rounded constant or a misprint |

A row's id is `<source id>:<key>`, such as `2011_zhang:3`. No 2 rows of a source have the same key, and the script stops on a source file in which they do: a key that the source repeats is written in `key` with a suffix `#2`, `#3`, ..., such as `key = 'Ex. 4.1#2'`, and a row added later takes the next free suffix, so that adding a row never changes the id of another row.

Every text field is markdown, with code in backticks; a field that holds only code, such as `interval = '[0, 1]'`, is written without them.

## Statuses

Each row has 1 of 3 final statuses, decided in this order; the paragraphs *The same function* and *Test functions and intervals* below the list define the terms that the list uses:

- **`incomplete`:** the source does not give enough to define a test function; every other row is complete. The row's reason starts with 1 of 4 cases:
  - `no interval`: the source gives no interval, or only starting points;
  - `no usable interval`: the interval text gives no interval with finite numeric bounds, such as prose (`an interval containing the origin`), a half-line (`theta > 0`), an infinite bound, or bounds without values (`[a, b]`);
  - `no function`: the source gives no function, or one that needs data that the source does not print, such as a sample; a function with random noise of a stated distribution counts as given;
  - `parameters without values`: a parameter of the function has no published value, such as an `eps` that is only "small".
- **`duplicate`:** earlier complete rows already give each of the row's test functions: the same function on the same interval with the same parameter values. `duplicate_of` names those earlier rows.
- **`new`:** every other complete row. That includes:
  - the same function on another interval or with other parameter values;
  - the same function in a form that rounds differently, such as a polynomial in expanded form compared with the same polynomial in factored or nested form, or 2 fixed-point forms `x = g(x)` of 1 equation.

A `new` or `incomplete` row names, in `derived_from`, the earlier rows whose function it copies or changes:

- the same function on other intervals or with other parameter values;
- the same model with other constants (`g = 9.8` against `9.81`);
- the same function shifted in `x`.

`derived_from` changes no status; it only adds edges between sources in `summary.md` and `timeline.html` (§ The summary and the page).

**The same function.** A row has the same function as another row when one is the other in 1 of these forms:

- written differently without changing how it is computed (reordered terms or factors, `x*x*x` against `x^3`);
- with its sign flipped, or multiplied by a constant;
- as an equation against its difference form (`sin(x) = x^2` against `sin(x) - x^2`).

Where a source misprints a function, the row is compared as the function that the source meant, and its notes say so.

**Test functions and intervals.** A row's function has 1 instance per combination of its parameter values. A row's test functions are the pairs of 1 instance and 1 of the row's intervals:

- An interval belongs to every instance, except an interval whose bounds use a parameter, such as `[0, (q - 1)/q]`, which belongs only to the instances with the same parameter values.
- Intervals are the same when their bounds are the same numbers: `(a, b)` and `[a, b]` are the same interval, and so are `[-1E4, 1E4]` and `[-10^4, 10^4]`, but `[0.5, sqrt(3)]` and `[0.5, 1.7320508]` are not.
- Where the interval text holds backticks, only the code between them gives intervals, so that a remark such as `(Ex. 5.3, 5.5)` is not read as one. A name that the text assigns in backticks, such as `` `n = 1, ..., 10` ``, gives values to bounds such as `[(n - 1)*pi, n*pi]`.

**Each row names the first appearance of its function:** a row that names a `duplicate`, in `duplicate_of` or `derived_from`, names the rows in that duplicate's `duplicate_of` instead. A duplicate never names an `incomplete` row, since that row gives no test function.

**How the script decides.** It parses each row's `f` and `parameters` with sympy into its instances, and its interval text into intervals; the docstrings of `matching.py` and `intervals.py` in `scripts/literature_test_problems/` give the comparisons.

The automatic status is `incomplete` where the `incomplete` condition below holds; otherwise `undecided` where any of the `undecided` conditions below holds; otherwise `duplicate` or `new`:

- **`incomplete`:** the interval text gives no usable interval, or the row has no code for its function (`f_description` without backticks);
- **`duplicate`:** earlier complete rows have each of its test functions, compared by structure: equal after an equation becomes its difference form, and after a constant factor and the sign are removed; a row whose `f` does not parse is compared by its text instead: its `f` or `f_description` and its `parameters`, ignoring whitespace and backticks;
- **`new`:** the row parses with a value for every parameter, and earlier complete rows lack some of its test functions; `derived_from` names each earlier row that has 1 of the row's instances, the row's family (its expression with its parameters as symbols) or the row's text;
- **`undecided`:** a person decides the status in `decisions.csv`. `match_kind` gives why:
  - `unparsed`: the `f` does not parse, and earlier rows with the same text lack some of its test functions;
  - `interval does not parse`;
  - `parameters without values`: an instance still holds a parameter as a symbol, because the script found no value for it; the source may give its values in a form that the script does not read;
  - `value`: some test functions are found only by value, with the same values up to a constant factor at fixed x-values, so the function may be the same or round differently;
  - `unpaired`: every test function is found, but some only in an earlier row of 1 of the 2 kinds below, for which the script may list test functions that the earlier source does not give:
    - a row with several instances and several intervals that the script cannot pair with each other;
    - a row whose parameters give several sets of values, separated by `;`, which the script combines into every possible combination;
  - `no test function`: no interval belongs to any instance, so the row has no test function.

## Decisions

`decisions.csv` holds 1 line per row that a person decided, with the columns `row_id`, `status`, `duplicate_of`, `derived_from` and `reason`. A decision replaces the script's automatic status, named rows and reason for that row, so it also corrects a wrong one.

A field with several row ids separates them by ` | `. A row decided `incomplete` gives no test functions that a later row could duplicate.

## The table of rows

`rows.csv` repeats each row's `f`, `f_description`, `parameters` and `interval`, and adds:

| column | content |
|---|---|
| `row_id`, `year`, `subcategory` | the row's id, and its source's year and subcategory |
| `parse_note` | why the script could not parse the row's `f` or interval, or how many of its intervals it left out as not usable; empty when both parsed |
| `n_instances` | the number of the row's parsed instances |
| `automatic_status` | the script's status |
| `match_kind` | the comparisons that found the rows in `matches`, the reason that a row is `incomplete`, or why a row is `undecided` |
| `matches` | the earlier rows that the script found |
| `status`, `duplicate_of`, `derived_from`, `reason` | the final status, the earlier rows that it names, and the reason, taken from `decisions.csv` where that file has a line for the row; an automatic `incomplete` row's reason is its `match_kind` |

## The summary and the page

An edge runs from an earlier source to a later one for every later row that names a row of the earlier source, in `duplicate_of` or `derived_from`; `summary.md` lists the edges into each source as *takes rows from*.

Short functions that many sources hold, such as `cos(x) - x`, would connect nearly every pair of sources, so they add no edges: a row is such a common function when later rows of at least `COMMON_MIN_SOURCES` sources name it and its `f` is at most `COMMON_MAX_LENGTH` characters long (both set in `scripts/literature_test_problems/overview.py`).

Common functions and the rows that name them still count in the row counts of their sources, and `summary.md` lists the common functions.

## Formulas

A formula is `active` while it holds a `new` row, and `retired` once it holds none. Every `new` row belongs to exactly 1 active formula of category 1, and that formula belongs to the row's source; `duplicate` and `incomplete` rows belong to no active formula.

By default, each `new` row is a formula of its own. A formula's id is `f<subcategory>.<source>.<formula>`, such as `f1.4.12.3`, formula 3 of source 12 of subcategory `1.4`.

**An id never changes once given.** The script keeps every id that `formulas.csv` already holds, and gives new ids only by appending:

- **Sources:** a source gets a number when it first has a `new` row: 1 more than the largest source number of its subcategory, retired formulas included. A source without a `new` row gets no number.
- **Formulas:** a new formula gets 1 more than the largest formula number of its source, retired formulas included.
- **Changed rows:** a formula keeps its id while its rows change, as long as it joins no other formula and does not split. A row that stops being `new` leaves the formula, and a row that becomes `new` can join the formula through `formula_decisions.csv`. The formula's `variable_change`, `f` and `parameters` can change too.
- **Retired formulas:** a formula that no longer holds a `new` row stays in `formulas.csv` as `retired`, so that its id is never given again. This happens, for example, when a source that is older but was added later holds the same functions, so that the formula's rows become `duplicate`. A retired formula becomes `active` again if the same rows become `new` again.
- **Retired lines keep their history:** the rows of a retired line may no longer exist, or may belong to an active formula; the script checks only active formulas against `rows.csv`.

Without a `formulas.csv`, the script numbers the sources of each subcategory in time order, and the formulas of each source in the order of its rows; a formula of several rows takes the position of its first row.

Deleting `formulas.csv` renumbers every formula in this way, which only a major release after 1.0.0 may do.

**A change that would change the id of a formula stops the script.** These changes do:

- a join: a formula that would hold the rows of 2 active formulas;
- a split: an active formula whose `new` rows would be in 2 formulas;
- an active formula that names a row that no longer exists;
- an active formula whose source is now in another subcategory.

The script then leaves `formulas.csv` as it is and reports the problem, and a person resolves it:

1. Decide which ids stay.
2. Edit `formulas.csv` by hand to match. Never delete a line: for each formula whose id does not stay, set its `status` to `retired`, so that its id is never given again.
3. Regenerate.

A join or split can also come from formulas that an earlier regeneration appended to `formulas.csv` but that are not committed yet, such as a new source's formulas from before its lines in `formula_decisions.csv`. Restore `formulas.csv` from git then, and regenerate.

`formula_decisions.csv` holds 1 line per formula that a person decided, with the columns `row_ids`, `variable_change`, `f`, `parameters` and `reason`. A line does 1 or both of these:

- **It puts several `new` rows of 1 source into 1 formula,** where they are obviously 1 function: the same expression, in which only the intervals and the values of at most 2 constants or parameters differ.
  - A varied constant must not change the kind of function, such as the degree of a polynomial, unless the source presents the rows as 1 family.
  - When in doubt, the rows stay separate formulas.
- **It changes the variable of 1 row's formula,** where the source prints its function in 1 variable but solves for another: the formula takes the variable that the source solves for, provided that the formula in that variable reproduces the source's results.
  - The row keeps the function as the source prints it, and `variable_change` describes the formula's variable in words, such as `` the pH, as `f(10^-pH)` on `[2, 12]` `` for a function `f(H)` that the source prints in `H`.

`row_ids` separates the formula's rows by ` | `, and `reason` says why the rows are 1 function, or how the formula in the new variable reproduces the source's results. A line of 1 row must give a `variable_change`, and a row is in at most 1 line.

**A line whose rows print 1 function, each row with its own values of some parameters, gives the formula's function**, which the formula modules need (§ Formula modules):

- `f` is the rows' function in its family form, with each value that differs between the rows as a parameter, such as `x^3 - a`. A parameter is not named `c`, which every formula uses for its shift along x.
- `parameters` gives each row's values of those parameters, in the order of `row_ids` and separated by ` | `, such as `a = 1 | a = -1`.

A line gives both or neither; a line whose rows give the same function and differ only in their intervals gives neither, and the formula takes the `f` of its first row.

Rows of different sources never share a formula, so that each formula's id credits the source that introduced its test functions.

A function in 2 forms that compute differently, such as a polynomial expanded and factored, gives 2 separate `new` rows, which stay separate formulas. A formula of several rows keeps each row's parameter values together with that row's intervals: it never combines 1 row's parameter values with another row's interval.

`formulas.csv` lists the formulas in id order, retired ones included, with the columns `formula_id`, `status`, `source_id`, `row_ids`, `variable_change`, `f` and `parameters`.

A formula's `status` is `active` or `retired`; `variable_change`, `f` and `parameters` copy those of the formula's line in `formula_decisions.csv`, with the sets of `parameters` in the order of the formula's rows.

## Formula modules

Each active formula of `formulas.csv` is a `Formula` in sunnbear's catalog, below `src/sunnbear/_core/functions/catalog/c01_published_test_functions/`: 1 package per subcategory, 1 package per source and 1 module per formula. A script generates the modules from the source files:

```
uv run python -m scripts.literature_test_problems.formula_modules <source id> ...
```

For each source named, the script writes the source's package and its formula modules, and rewrites the `__init__.py` of each subcategory. A generated formula module:

- evaluates the formula's function at `x - (b - a)*c`, where `[a, b]` is the formula's interval: the formula's `c` shifts the function along x by a multiple of the interval's width. The function is the `f` of the formula's first row, as the source prints it, unless the formula's line in `formulas.csv` gives an `f`;
- lists the formula's published test functions in a `ParamTable`: 1 tuple per combination of parameter values and interval that the rows give, and a formula with several intervals takes their bounds as 2 more parameters, `a` and `b`;
- names its source in a `FormulaSource`: the source's `reference`, and the keys of the formula's rows as the location;
- holds test cases whose expected values mpmath computes from the function;
- holds `SURVEY_FIELDS_HASH`, a hash of the fields that the module depends on: the source's `title` and `reference`, the formula's `variable_change`, `f` and `parameters` in `formulas.csv`, and the fields of its rows, so that the hash changes with each change of those fields.

**The function** may use, besides the operators and the functions of Python's `math`, the constructs that the docstring of `formula_expressions.py` lists, such as `if(condition; a; b)`, `sum(term, i = m..n)` and the Bessel functions.

**The published test functions:** a row's parameters give 1 or several sets of values:

- **1 set:** each combination of its values pairs with each of the row's intervals.
- **Several sets,** separated by `;`, where the same parameter gets values in more than 1 set: each set names its intervals after `on`, as in `` on `[0, 5]`: `a = 0.2, 1`, `n = 4(2)12`; on `[-0.95, 4.05]`: `a = 1`, `n = 8(2)14` ``, unless the row gives only 1 interval.

For a formula of several rows, the script checks that each row's own `f`, at that row's values, gives the formula's function.

**A value that needs more than 12 significant digits,** such as `pi`, is rounded to 12, the most that a parameter value holds; this applies to a parameter value and to a bound of a formula with several intervals.

The module's docstring names each rounded value, and its test cases evaluate the function at the rounded value.

**A test case whose function is ill-conditioned,** such as `sin(x*10^6)`, gets a wider `atol`, which `FormulaModuleSpec._find_case` in `scripts/literature_test_problems/formula_modules.py` sets:

- **When:** the test case's Python value differs from mpmath's by more than `CASE_ATOL`, but by no more than the spread of the function's exact values within `CASE_X_ULPS` float64 steps of x on either side.
- **Value:** a multiple of that spread.

The modules of 2 kinds of formulas are written by hand, and the script only imports them:

- a formula with a row that gives only an `f_description`;
- a formula in the script's `UNTRANSLATABLE_FORMULAS`, whose row's `f` the script cannot translate, such as an infinite sum.

The script stops and names each formula that it cannot generate. It cannot generate:

- a formula with a `variable_change`;
- a function, parameter values or intervals that it cannot read, such as a parameter without a published value, or several sets of values with several intervals and no `on`;
- a formula of several rows in which a row's own `f` differs from the formula's function;
- a function that is complex at an x-value of a test case, or whose Python value agrees with mpmath at none of the x-values tried.

After a change of a source file, regenerate the modules of its formulas: the tests recompute each module's `SURVEY_FIELDS_HASH` from the source files, so that a module that was not regenerated fails the tests.

## Adding a source

1. Write `sources/<id>.toml`. Add a relation where a reader needs to know how its rows relate to another source's rows, such as a block of functions that the new source copies with changes; `duplicate_of` and `derived_from` already name every earlier row that the script finds.
2. Regenerate. The script prints each row that needs a decision; `rows.csv` gives, in `match_kind` and `matches`, why it needs one and the earlier rows that the script found for it.
3. Add a line to `decisions.csv` for each of those rows, and for any automatic status that is wrong, then regenerate until the script prints no problems.
4. Add a line to `formula_decisions.csv` for each set of the source's `new` rows that are obviously 1 function, with `f` and `parameters` where each row gives its own values of a parameter, and for each row whose formula takes another variable (§ Formulas). Restore `formulas.csv` from git, because the regenerations above already appended the source's formulas without these decisions, then regenerate.
5. Generate the source's formula modules (§ Formula modules), and write by hand the modules of its formulas whose rows give only an `f_description`, or whose `f` the script cannot translate (add those to its `UNTRANSLATABLE_FORMULAS`).
6. Commit the source file, `decisions.csv`, `formula_decisions.csv`, the generated files and the formula modules together.

## Regenerating

Run the script from the repo root, with the dev dependencies installed:

```
uv run python -m scripts.literature_test_problems
```

The script:

- writes the generated files;
- prints the counts per status, the numbers of active and retired formulas, and every problem that it finds;
- exits with status 1 if there is a problem.

It needs sympy, from the dev dependency group, and a Unix system, because it limits the time of parsing each row with `SIGALRM`.

CI does not regenerate `rows.csv`, because another sympy version could change a match. Instead, `tests/scripts/test_literature_test_problems.py` checks, without running the matching, that:

- `rows.csv` holds exactly the rows of the source files;
- every decision is applied, and every final status follows its rules (§ Statuses): no row names an unknown or a later row, and no duplicate names an `incomplete` row;
- every source file has its fields;
- `summary.md` and `timeline.html` equal what the script builds from `rows.csv` and the source files;
- the active formulas of `formulas.csv` hold every `new` row exactly once and no other row, the rows of each formula come from its own source, and the file equals what the script builds from `rows.csv`, `formula_decisions.csv` and the file's own ids;
- each formula of category 1 in sunnbear's catalog has an active line in `formulas.csv`; its category is named after its source, its `source` holds the source's reference and its rows' keys as the location, and a generated module holds the current `SURVEY_FIELDS_HASH`;
- every active formula of a source that has a formula in the catalog is in the catalog too.

A change to the parsing or matching in `scripts/literature_test_problems/`, or to the sympy version, is what the test does not check: whoever makes it regenerates `rows.csv`.
