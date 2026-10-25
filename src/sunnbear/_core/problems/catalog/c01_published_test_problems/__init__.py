"""This category holds the test problems of published sources, grouped by kind of source, then by source."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_articles_of_solvers_that_sunnbear_implements,
    c02_articles_of_other_solvers,
    c03_public_benchmark_suites,
    c04_textbooks,
)


class PublishedTestProblems(FormulaCategory):
    """`PublishedTestProblems` is the top-level category of formulas taken from published sources.

    Each formula of this category evaluates its published function at ``x - c_scale*c``, where ``c_scale`` is the
    rounded width of the formula's interval, so that ``c`` shifts the function along x, and at ``c = 0`` the formula is
    the published function.

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

    A formula with the parameter ``modified`` follows these rules where ``modified = 0``.

    Some published test problems do not satisfy the benchmark suite inclusion conditions, the conditions on every test
    problem of a benchmark suite. Where ``modified = 1``, the formula gives a modified version of such a published test
    problem. The benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`, checks these conditions.

    An example is a published test problem whose function is not defined left of its interval: a shift along x by any
    ``c > 0`` evaluates that function outside its domain.

    The value of ``modified`` is the level of modification, and a formula may also have higher levels, ``modified = 2``
    and up. Each level exists only where a test problem of the level below does not satisfy the conditions, and applies
    the modification of the level below plus 1 more.

    The formula's docstring describes its modifications, which keep the modified test problems as close to the
    published test problems as the benchmark suite inclusion conditions allow.

    Where a modification changes what the published test problem tests, such as when it removes a feature that the
    source uses the test problem to show, the formula's docstring says so in a paragraph with the words "changes what
    the test problem tests".
    """

    number = (1,)
    name = "Published test problems"
    is_builtin_only = True

    @staticmethod
    def c_scale(a: float, b: float) -> float:
        """Return the ``c_scale`` of the interval ``[a, b]``: its width, rounded to 3 significant digits."""
        return float(f"{b - a:.3g}")
