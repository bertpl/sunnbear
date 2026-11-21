import pytest

from sunnbear._core.problems.core import FormulaParam


def test_param_holds_its_declarations():
    """A parameter holds its name, its symbol and its meaning; the symbol and the meaning default to None."""
    # --- arrange / act ----------------
    declared = FormulaParam("alpha", latex_symbol=r"\alpha", meaning=r"the exponent at $\x = 0$")
    default = FormulaParam("m")

    # --- assert -----------------------
    assert (declared.name, declared.latex_symbol, declared.meaning) == ("alpha", r"\alpha", r"the exponent at $\x = 0$")
    assert (default.latex_symbol, default.meaning) == (None, None)


@pytest.mark.parametrize("name", ["", "1x", "a-b", "a b"])
def test_param_name_must_be_an_identifier(name):
    """A name that is no Python identifier, which a hook's signature cannot hold, is rejected."""
    with pytest.raises(ValueError, match="Python identifier"):
        FormulaParam(name)
