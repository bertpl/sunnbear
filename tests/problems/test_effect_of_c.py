import pytest

from sunnbear._core.problems.core import EffectOfC
from tests.problems.effect_of_c_check import follows_effect_of_c
from tests.problems.example_formulas import ExampleCubic, ExampleOddPower


def test_every_member_has_a_sentence():
    """Each way of applying ``c`` gives its sentence for a reader."""
    assert [effect.sentence for effect in EffectOfC] == [
        "Shifts the function along the x-axis.",
        "Shifts the function along the y-axis.",
        "Scales the function along the x-axis.",
    ]


@pytest.mark.parametrize("formula_cls", [ExampleCubic, ExampleOddPower])
@pytest.mark.parametrize("effect", list(EffectOfC))
def test_check_accepts_only_the_declared_way(formula_cls, effect):
    """The evaluation check accepts the way that the example formula follows, and rejects the other ways."""
    # --- arrange ----------------------
    candidate = formula_cls().build_all_candidates()[-1]

    # --- act / assert -----------------
    assert follows_effect_of_c(candidate, effect) == (effect is formula_cls.effect_of_c)
