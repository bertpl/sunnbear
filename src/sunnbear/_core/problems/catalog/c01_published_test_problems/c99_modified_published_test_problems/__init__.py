"""This category holds the modified versions of published test problems, grouped like the rest of category 1."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_articles_of_solvers_that_sunnbear_implements,
    c02_articles_of_other_solvers,
    c03_public_benchmark_suites,
    c04_textbooks,
)


class ModifiedPublishedTestProblems(FormulaCategory):
    """`ModifiedPublishedTestProblems` is subcategory 1.99, the modified versions of published test problems.

    Some published test problems do not satisfy the benchmark suite inclusion conditions, the conditions on every test
    problem of a benchmark suite. The benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`, checks
    these conditions.

    An example is a published test problem whose function is not defined left of its interval: a shift along x by any
    ``c > 0`` evaluates that function outside its domain.

    Formula 1.99.x.y.z modifies formula 1.x.y.z, and has the same name and `source`; subcategories 1.99.x and 1.99.x.y
    have the names of subcategories 1.x and 1.x.y.

    Each formula holds 1 modification, which keeps the test problems as close to the published ones as the conditions
    allow. A modification may combine several changes where 1 change alone leaves a test problem that does not satisfy
    the conditions; the formula's docstring then states why each change is needed.

    A formula holds either every parameter tuple of the published formula, including tuples whose published test
    problem satisfies the conditions, or only the tuples that need the modification; a formula that holds only some
    tuples names them in its docstring.

    A formula of this subcategory applies ``c`` in 1 of 3 ways, which its docstring states:

    - it shifts x by ``c_scale*c``, as the published formulas do, with ``c_scale`` the rounded width of the formula's
      own interval;
    - it adds ``c`` to the function's value, on the published interval, and does not shift x;
    - it keeps the published interval ``[a, b]`` and evaluates the function at ``x*exp(-c*ln(b/a))``: ``c`` scales x,
      so that the root moves by the factor ``(b/a)**c`` and never reaches 0.

    Where a modification changes what the published test problem tests, such as when it removes a feature that the
    source uses the test problem to show, the formula's docstring says so in a paragraph with the words "changes what
    the test problem tests".

    `REJECTED_PUBLISHED_TEST_PROBLEMS.md`, in this package, lists every published test problem that the benchmark
    suite pipeline rejects, and the decision for it: a modification in this subcategory, or the reason for none.
    """

    number = (1, 99)
    name = "Modified published test problems"
