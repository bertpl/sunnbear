"""This category holds the test problems of published sources, grouped by kind of source, then by source."""

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

    Each formula of subcategories 1.1 to 1.4 evaluates its published function at ``x - c_scale*c``, where ``c_scale``
    is the rounded width of the formula's interval, so that ``c`` shifts the function along x, and at ``c = 0`` the
    formula is the published function.

    A shift along x keeps the function's shape around its root; a shift of its values, ``f(x) - c``, would turn a
    multiple root into a simple one.

    ``c_scale`` is the width of the formula's interval ``[a, b]``, rounded to 3 significant digits. Scaling by the
    width means that, for every formula, the values of ``c`` that keep a root inside the interval span a range of
    about 1.

    The rounding changes that range by at most 0.5%, and keeps long numbers out of the formula modules, such as
    ``1.9999999999999996`` for the width of ``[2.6, 4.6]``.

    - A formula with 1 interval writes ``c_scale`` as a number.
    - A formula with several intervals takes ``c_scale`` as a parameter after ``a`` and ``b``, and each parameter
      tuple holds the ``c_scale`` of its own interval, so that ``parametrized_fun`` does not round the width on every
      call.

    Subcategory 1.99 holds the modified versions of published test problems that do not satisfy the benchmark suite
    inclusion conditions; its docstring states how its formulas apply ``c``.
    """

    number = (1,)
    name = "Published test problems"
    is_builtin_only = True

    @staticmethod
    def c_scale(a: float, b: float) -> float:
        """Return the ``c_scale`` of the interval ``[a, b]``: its width, rounded to 3 significant digits."""
        return float(f"{b - a:.3g}")
