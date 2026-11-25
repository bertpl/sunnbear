"""This category holds the test problems of published sources, grouped by kind of source, then by source."""

import math

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_articles_of_solvers_that_sunnbear_implements,
    c02_articles_of_other_solvers,
    c03_public_benchmark_suites,
    c04_textbooks,
    c99_modified_published_test_problems,
)


class PublishedTestProblems(FormulaCategory):
    """`PublishedTestProblems` is the top-level category of formulas taken from published sources.

    Each test problem of this category is a root-bracketing problem on its interval, whatever the source uses the
    function for, such as finding every root in an interval, minimizing the function, or iterating to a fixed point.

    Each formula of category 1 outside subcategory 1.99 evaluates its published function at ``x - c_scale*c``, where
    ``c_scale`` is the width of the formula's interval rounded to the nearest power of 10, so that ``c`` shifts the
    function along x, and at ``c = 0`` the formula is the published function.

    A shift along x keeps the function's shape around its root; a shift of its values, ``f(x) - c``, would turn a
    multiple root into a simple one.

    ``c_scale`` is the power of 10 nearest the width of the formula's interval ``[a, b]`` on a log scale, so the width
    lies between about 0.32 and 3.2 times ``c_scale``, and the values of ``c`` that keep a root inside the interval span
    a range whose length lies between about 0.3 and 3.

    A power of 10 shows a reader that the scale's exact value does not matter: the benchmark suite pipeline calibrates
    the range of ``c`` of each test problem, whatever its scale.

    - A formula that shifts x and has 1 interval writes ``c_scale`` as a number.
    - A formula that shifts x and has several intervals takes ``c_scale`` as a parameter after ``a`` and ``b``, and
      each parameter tuple holds the ``c_scale`` of its own interval, so that ``parametrized_fun`` does not compute
      the scale on every call.

    A person writes each formula module outside subcategory 1.99 from the formula's rows in the survey of published
    test problems, `data/literature_test_problems/sources/`, so a change of a formula's rows needs a change of its
    module.

    Subcategory 1.99 holds modified versions of the published test problems that do not satisfy the benchmark suite
    inclusion conditions; the docstring of `ModifiedPublishedTestProblems` states how the formulas of subcategory 1.99
    apply ``c``, and a formula of subcategory 1.99 that shifts x follows the rules above.
    """

    number = (1,)
    name = "Published test problems"
    description = (
        "The test problems come from articles on root-finding methods, public benchmark suites and textbooks. A "
        r"formula that shifts its function along the x-axis evaluates the function at $\x - s \c$, with $s$ the width "
        "of each published interval, rounded to the nearest power of 10 on a log scale."
    )
    is_builtin_only = True

    @staticmethod
    def c_scale(a: float, b: float) -> float:
        """Return the ``c_scale`` of the interval ``[a, b]``: the power of 10 nearest its width on a log scale."""
        return 10.0 ** round(math.log10(b - a))
