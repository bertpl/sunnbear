import pytest

from sunnbear._core.problems.core import PLAIN_MARKER_MACROS, LatexTemplate


# ==================================================================================================
#  Names in the text
# ==================================================================================================
def test_placeholder_names_follow_their_first_use():
    """A template lists each parameter that its placeholders name once, in the order of first use."""
    # --- arrange / act ----------------
    template = LatexTemplate(r"\param{m} \x + (1 - \param{m}) \x^{\param{p}} + \c")

    # --- assert -----------------------
    assert template.placeholder_names == ("m", "p")


def test_marker_names_follow_their_first_use():
    r"""A template lists the arguments of its ``\tmp`` and ``\fn`` markers, with 1 level of braces in an argument."""
    # --- arrange / act ----------------
    template = LatexTemplate(r"\fn{g}(\tmp{u}) + \tmp{t_{1}} \tmp{u} / \fn{g}(\param{b})")

    # --- assert -----------------------
    assert template.temporary_variables_and_functions == (("tmp", "u"), ("tmp", "t_{1}"), ("fn", "g"))


@pytest.mark.parametrize(
    "text",
    [
        r"\param{1m} \x",  # the name is no identifier
        r"\param m",  # the name has no braces
        r"\tmp u",
        r"\fn{} + \x",  # the argument is empty
    ],
)
def test_malformed_command_is_rejected(text):
    r"""A ``\param``, ``\tmp`` or ``\fn`` without a well-formed argument is rejected when the template is built."""
    with pytest.raises(ValueError, match="no well-formed argument"):
        LatexTemplate(text)


def test_longer_command_is_not_a_marker():
    r"""A LaTeX command whose name only starts with a marker's name, such as ``\fnsymbol``, is not a marker."""
    # --- arrange / act ----------------
    template = LatexTemplate(r"\fnsymbol{1} + \tmpx")

    # --- assert -----------------------
    assert template.temporary_variables_and_functions == ()


# ==================================================================================================
#  Substitution
# ==================================================================================================
def test_substitute_wraps_each_replacement_in_prm():
    r"""Each placeholder becomes its LaTeX wrapped in ``\prm{…}``, and every other part of the text stays."""
    # --- arrange ----------------------
    template = LatexTemplate(r"\param{m} \x + (1 - \param{m}) \x^{\param{p}} + \c")

    # --- act --------------------------
    latex = template.substitute({"m": "(-0.5)", "p": "3", "unused": "w"})

    # --- assert -----------------------
    assert latex == r"\prm{(-0.5)} \x + (1 - \prm{(-0.5)}) \x^{\prm{3}} + \c"


def test_substitute_rejects_a_missing_name():
    """A placeholder whose name the substitutions do not hold is reported."""
    with pytest.raises(ValueError, match=r"\['p'\]"):
        LatexTemplate(r"\param{m} \x^{\param{p}}").substitute({"m": "m"})


@pytest.mark.parametrize(
    "text, expected",
    [
        # a value after a digit, another value or an exponent gets a dot
        (r"1.5 \param{a} \x", r"1.5 \cdot \prm{2} \x"),
        (r"\frac{1}{2 \param{a} + 1}", r"\frac{1}{2 \cdot \prm{2} + 1}"),
        (r"\param{a} \param{b}", r"\prm{2} \cdot \prm{(-3)}"),
        (r"\param{a}^2 \param{b}", r"\prm{2}^2 \cdot \prm{(-3)}"),
        (r"\tmp{u}^{2} \param{b}", r"\tmp{u}^{2} \cdot \prm{(-3)}"),
        # a value after anything else gets none
        (r"\x^{\param{a}} - \param{b} (\param{a} + \c)", r"\x^{\prm{2}} - \prm{(-3)} (\prm{2} + \c)"),
        (r"\text{if } \param{a} \text{ is odd}", r"\text{if } \prm{2} \text{ is odd}"),
        (r"\log_2 \param{a}", r"\log_2 \prm{2}"),
    ],
)
def test_substitute_values_separates_a_value_from_a_number_before_it(text, expected):
    r"""A value after a number gets ``\cdot`` before it, and a value after anything else gets none."""
    # --- act --------------------------
    latex = LatexTemplate(text).substitute_values({"a": "2", "b": "(-3)"})

    # --- assert -----------------------
    assert latex == expected


def test_plain_marker_macros_define_every_marker():
    """The plain definitions cover the 5 markers, each as plain LaTeX."""
    assert dict(PLAIN_MARKER_MACROS) == {r"\x": "x", r"\c": "c", r"\tmp": "#1", r"\fn": "#1", r"\prm": "#1"}
