"""This category holds the test functions of published sources, grouped by kind of source, then by source."""

from sunnbear._core.functions.core import FormulaCategory

from . import (
    c01_articles_of_solvers_that_sunnbear_implements,
    c02_articles_of_other_solvers,
    c03_public_benchmark_suites,
    c04_textbooks,
)


class PublishedTestFunctions(FormulaCategory):
    """`PublishedTestFunctions` is the top-level category of formulas taken from published sources.

    Each formula of this category evaluates its published function at ``x - c_scale*c``, so that ``c`` shifts the
    function along x, and at ``c = 0`` the formula is the published function. A shift along x keeps the function's
    shape around its root; a shift of its values, ``f(x) - c``, would turn a multiple root into a simple one.

    ``c_scale`` is the width of the formula's interval ``[a, b]``, rounded to 3 significant digits. Scaling by the
    width makes the range of ``c`` that keeps a root inside the interval about 1 wide for every formula. The rounding
    changes that range by at most 0.5%, and keeps long numbers out of the code, such as ``1.9999999999999996`` for the
    width of ``[2.6, 4.6]``.

    - A formula with 1 interval writes ``c_scale`` as a number.
    - A formula with several intervals takes ``c_scale`` as a parameter after ``a`` and ``b``, with each parameter
      tuple's own value.
    """

    number = (1,)
    name = "Published test functions"
    is_builtin_only = True
