"""This package declares the parameter ``c_scale`` of the formulas of category 1 that have several intervals.

The class docstring of `PublishedTestProblems` states the rule for ``c_scale``; each of those formulas declares
`C_SCALE_PARAM` among its `params`, so that its symbol and its meaning for a reader are written once.
"""

from sunnbear._core.problems.core import FormulaParam

C_SCALE_PARAM = FormulaParam(
    "c_scale",
    latex_symbol="s",
    meaning=(
        r"The shift of x is $\param{c_scale}$ times $\c$, where $\param{c_scale}$ is the width $\param{b} - \param{a}$ "
        r"of the interval, rounded to 3 significant digits."
    ),
)
