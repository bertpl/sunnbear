"""`define_formula_cls` defines formulas without parameters for the tests of the validation stage."""

from sunnbear._core.problems.core import Formula, ParamRecipe, XCFun


def define_formula_cls(formula_number: tuple[int, ...], xc_fun: XCFun, a: float, b: float) -> type[Formula]:
    """Define and return a formula without parameters, numbered `formula_number`, that evaluates `xc_fun` on [a, b]."""

    class ExampleFormula(Formula):
        number = formula_number
        name = f"Example {formula_number}"
        jit = False
        parametrized_fun = staticmethod(xc_fun)

        def interval_bounds(self) -> tuple[float, float]:
            """Return the interval ``[a, b]``."""
            return (a, b)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            """Return no recipes; the formula has no parameters."""
            return ()

    return ExampleFormula
