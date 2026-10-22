import math

import pytest
from counted_float import FlopCountingContext

from sunnbear.functions import FormulaRegistry, ParamRecipe, ParamTable, XShiftedFormula


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _define_sine(last_number: int, interval_kind: str) -> type[XShiftedFormula]:
    """Define an `XShiftedFormula` of ``sin(n*x) - 0.5`` with a fixed interval, or one that depends on ``n``."""

    class Sine(XShiftedFormula):
        """``sin(n*x) - 0.5``."""

        number = (99, last_number)
        name = f"Sine {last_number}"
        param_names = ("n",)

        @staticmethod
        def unshifted_fun(x: float, n: float) -> float:
            return math.sin(n * x) - 0.5

        @staticmethod
        def interval_bounds(n: float) -> tuple[float, float]:
            if interval_kind == "fixed":
                return (0.0, 1.5)
            else:
                return (0.0, 2.0 * n)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return (ParamTable(names=("n",), rows=((1.0,), (0.5,))),)

    return Sine


# ==================================================================================================
#  The shift
# ==================================================================================================
@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("interval_kind, width", [("fixed", 1.5), ("depends on n", 1.0)])
def test_parametrized_fun_shifts_the_unshifted_fun_by_the_interval_width(interval_kind, width):
    """`parametrized_fun` evaluates `unshifted_fun` at ``x - (b - a)*c``, also inside a solve's flop counting."""
    # --- arrange ----------------------
    formula = _define_sine(990 if interval_kind == "fixed" else 991, interval_kind)()
    xc_fun = formula.bind_xc_fun((0.5,))

    # --- act --------------------------
    with FlopCountingContext():
        value = xc_fun(0.3, 0.25)

    # --- assert -----------------------
    assert value == math.sin(0.5 * (0.3 - width * 0.25)) - 0.5
    assert formula.parametrized_fun(0.3, 0.0, 0.5) == formula.unshifted_fun(0.3, 0.5)


@pytest.mark.usefixtures("isolated_registry")
def test_formula_without_jit_keeps_the_built_parametrized_fun():
    """With `jit = False`, the compiled function is the `parametrized_fun` that the class built."""
    # --- arrange ----------------------
    formula_cls = _define_sine(992, "fixed")
    formula_cls.jit = False

    # --- act / assert -----------------
    assert formula_cls()._compiled_formula() is formula_cls.parametrized_fun


# ==================================================================================================
#  Validation
# ==================================================================================================
@pytest.mark.usefixtures("isolated_registry")
def test_subclass_without_unshifted_fun_stays_abstract():
    """A subclass that does not implement `unshifted_fun` gets no `parametrized_fun` and no registration."""

    # --- arrange / act ----------------
    class Intermediate(XShiftedFormula):
        number = (99, 993)
        name = "Intermediate"

    # --- assert -----------------------
    assert getattr(Intermediate.parametrized_fun, "__isabstractmethod__", False)
    assert (99, 993) not in {formula.number for formula in FormulaRegistry.formulas()}


@pytest.mark.usefixtures("isolated_registry")
def test_interval_bounds_must_be_a_staticmethod():
    """`interval_bounds` as a plain method is rejected at class definition."""
    # --- act / assert -----------------
    with pytest.raises(TypeError, match="must be a @staticmethod"):

        class PlainIntervalBounds(XShiftedFormula):
            number = (99, 994)
            name = "Plain interval bounds"

            @staticmethod
            def unshifted_fun(x: float) -> float:
                return x

            def interval_bounds(self) -> tuple[float, float]:
                return (-1.0, 1.0)

            def recipes(self) -> tuple[ParamRecipe, ...]:
                return ()


@pytest.mark.usefixtures("isolated_registry")
@pytest.mark.parametrize("param_name", ["lower", "c"])
def test_parameter_named_like_a_name_of_the_template_is_rejected(param_name):
    """A parameter may not take a name that the generated `parametrized_fun` uses itself."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="cannot take"):

        class Clash(XShiftedFormula):
            number = (99, 995)
            name = "Clash"
            param_names = (param_name,)

            @staticmethod
            def unshifted_fun(x: float, p: float) -> float:
                return x - p

            @staticmethod
            def interval_bounds(p: float) -> tuple[float, float]:
                return (-1.0, 1.0)

            def recipes(self) -> tuple[ParamRecipe, ...]:
                return ()


@pytest.mark.usefixtures("isolated_registry")
def test_unshifted_fun_must_name_the_declared_parameters():
    """An `unshifted_fun` whose parameter names differ from `param_names` fails the formula's validation."""

    # --- arrange ----------------------
    class Misnamed(XShiftedFormula):
        number = (99, 996)
        name = "Misnamed"
        param_names = ("n",)

        @staticmethod
        def unshifted_fun(x: float, m: float) -> float:
            return x - m

        @staticmethod
        def interval_bounds(n: float) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return (ParamTable(names=("n",), rows=((0.5,),)),)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="unshifted_fun takes"):
        Misnamed().build_all_candidates()
