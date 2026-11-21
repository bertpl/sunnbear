import pytest

from sunnbear._core.problems.core import FormulaPresentation


# ==================================================================================================
#  Definitions
# ==================================================================================================
def test_definitions_used_in_order_are_accepted():
    """A temporary variable and an intermediate function, each defined before it is used, make a valid presentation."""
    # --- arrange / act ----------------
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"), (r"\fn{g}(\x)", r"\sinh \x")),
        expression=r"\fn{g}(\tmp{u}) / \fn{g}(\param{b})",
        interval=r"[0, \param{b}]",
        summary=r"Hyperbolic sine, scaled to 1 at $\x = \param{b}$.",
    )

    # --- assert -----------------------
    assert [template.text for template in presentation.templates] == [
        r"\tmp{u}",
        r"\x - \c",
        r"\fn{g}(\x)",
        r"\sinh \x",
        r"\fn{g}(\tmp{u}) / \fn{g}(\param{b})",
        r"[0, \param{b}]",
        r"Hyperbolic sine, scaled to 1 at $\x = \param{b}$.",
    ]


@pytest.mark.parametrize(
    "definitions, expression, message",
    [
        (((r"\x - \c", r"\x"),), r"\x", "exactly 1 name"),  # a left side that defines nothing
        (((r"\tmp{u} \tmp{v}", r"\x"),), r"\tmp{u} \tmp{v}", "exactly 1 name"),  # a left side that defines 2 names
        (((r"\tmp{v}", r"\tmp{u}"), (r"\tmp{u}", r"\x")), r"\tmp{v}", "no earlier definition"),  # used before defined
        (((r"\tmp{u}", r"\x"), (r"\tmp{u}", r"\c")), r"\tmp{u}", "an earlier line defines"),  # defined twice
        (((r"\tmp{u}", r"\x"),), r"\x - \c", "never used"),
        ((), r"\tmp{u} - \c", "no earlier definition"),  # used, never defined
        (((r"\tmp{g}", r"\x"),), r"\fn{g}(\x)", "no earlier definition"),  # a function is not a temporary variable
    ],
)
def test_invalid_definitions_are_rejected(definitions, expression, message):
    """A presentation whose definitions do not define each name once, before its use, is rejected when it is built."""
    with pytest.raises(ValueError, match=message):
        FormulaPresentation(definitions=definitions, expression=expression, interval="[0, 1]")


@pytest.mark.parametrize(
    "texts, message",
    [
        ({"notes": (r"Here $\tmp{u}$ is undefined.",)}, "no earlier definition"),  # a note names an undefined name
        ({"summary": r"A function of $\param{}$."}, "no well-formed argument"),  # malformed notation in the summary
    ],
)
def test_invalid_text_is_rejected(texts, message):
    """A text for a reader that names an undefined name, or breaks sunnbear's LaTeX notation, is rejected."""
    with pytest.raises(ValueError, match=message):
        FormulaPresentation(expression=r"\x - \c", interval="[0, 1]", **texts)
