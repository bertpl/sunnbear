r"""`FormulaPresentation` holds what a reader sees of a formula: its expression and interval, summary and notes.

Every field is written in sunnbear's LaTeX notation, which `latex_template` describes. `Formula` renders the fields with
its parameters' symbols, or with a test problem's values.
"""

from dataclasses import dataclass

from .latex_template import LatexTemplate


# ==================================================================================================
#  FormulaPresentation
# ==================================================================================================
@dataclass(frozen=True)
class FormulaPresentation:
    r"""`FormulaPresentation` holds a formula's expression and interval in LaTeX, its summary and its notes.

    An expression that uses temporary variables or intermediate functions lists them in `definitions`. `Formula` joins
    the definitions and the expression into 1 aligned display, so no field writes the ``\\`` or ``&`` that separate and
    align those lines.

    Attributes:
        expression: The right side of ``f(x, c) = …``, as the formula's code computes it, guards included. It may span
            several lines, such as a ``cases`` environment.
        interval: The interval, such as ``r"[-\param{b}, \param{b}]"``.
        definitions: The temporary variables and intermediate functions that the expression uses, in order, each as a
            pair of its left side and its right side, such as ``(r"\tmp{u}", r"\x - \c")`` or
            ``(r"\fn{g}(\x)", r"\sinh \x")``. A left side defines exactly 1 name, with 1 ``\tmp{…}`` or ``\fn{…}``
            marker. Empty by default.
        summary: Briefly, what the formula is, or what makes it an interesting test problem, such as "Oscillatory
            function with many roots". None by default; the catalog's tests require it of every shipped formula.
        notes: Paragraphs for a reader, such as a note that states the expression that the formula models, when its
            code computes an equivalent form of it. Empty by default.
    """

    expression: str
    interval: str
    definitions: tuple[tuple[str, str], ...] = ()
    summary: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        r"""Check the notation of every field, and that each temporary variable and function is defined before its use.

        Raises:
            ValueError: If a field breaks sunnbear's LaTeX notation (`LatexTemplate`); if a left side does not define
                exactly 1 name; if a name is defined twice, used before its definition, or defined and never used.
        """
        defined: list[tuple[str, str]] = []
        unused: set[tuple[str, str]] = set()
        for left_side, right_side in self.definitions:
            left_names = LatexTemplate(left_side).markers_and_names
            if len(left_names) != 1:
                raise ValueError(
                    f"FormulaPresentation: the left side {left_side!r} must define exactly 1 name, with 1 "
                    "\\tmp{…} or \\fn{…} marker."
                )
            self._check_names_are_defined(LatexTemplate(right_side), defined, f"the definition of {left_side!r}")
            unused -= set(LatexTemplate(right_side).markers_and_names)
            if left_names[0] in defined:
                raise ValueError(f"FormulaPresentation: {left_side!r} defines a name that an earlier line defines.")
            defined.append(left_names[0])
            unused.add(left_names[0])
        for text in (self.expression, self.interval, *self.texts_for_a_reader):
            self._check_names_are_defined(LatexTemplate(text), defined, f"the text {text!r}")
            unused -= set(LatexTemplate(text).markers_and_names)
        if unused:
            raise ValueError(f"FormulaPresentation: the definitions of {sorted(unused)} are never used.")

    # --------------------------------------------------------------------------
    #  Fields by kind
    # --------------------------------------------------------------------------
    @property
    def display_lines(self) -> tuple[tuple[str, str], ...]:
        r"""Return the lines of the display, as pairs of left and right side: the definitions, then ``f(\x, \c)``."""
        return (*self.definitions, (r"f(\x, \c)", self.expression))

    @property
    def math_templates(self) -> tuple[LatexTemplate, ...]:
        """Return the fields that are LaTeX: each side of each definition, the expression and the interval."""
        sides = [side for definition in self.definitions for side in definition]
        return tuple(LatexTemplate(text) for text in (*sides, self.expression, self.interval))

    @property
    def texts_for_a_reader(self) -> tuple[str, ...]:
        """Return the summary, where given, and the notes."""
        summary = (self.summary,) if self.summary is not None else ()
        return (*summary, *self.notes)

    @property
    def templates(self) -> tuple[LatexTemplate, ...]:
        """Return every field as a `LatexTemplate`: the fields that are LaTeX, then the texts for a reader."""
        return (*self.math_templates, *(LatexTemplate(text) for text in self.texts_for_a_reader))

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _check_names_are_defined(template: LatexTemplate, defined: list[tuple[str, str]], where: str) -> None:
        """Raise `ValueError` if `template` uses a temporary variable or function that `defined` does not hold."""
        undefined = [name for name in template.markers_and_names if name not in defined]
        if undefined:
            raise ValueError(f"FormulaPresentation: {where} uses {undefined}, which no earlier definition defines.")
