"""`FormulaPresentation` holds what a reader sees of a formula; the package's docstring says how it is rendered."""

from dataclasses import dataclass

from .latex_template import LatexTemplate


# ==================================================================================================
#  FormulaPresentation
# ==================================================================================================
@dataclass(frozen=True)
class FormulaPresentation:
    r"""`FormulaPresentation` holds a formula's definitions, expression and interval in LaTeX, its summary and notes.

    An expression that uses temporary variables or intermediate functions lists them in `definitions`. `Formula` joins
    the definitions and the expression into 1 aligned display, so no field contains the ``\\`` or ``&`` that separate
    and align those lines; an environment inside a field, such as ``cases``, keeps its own.

    Each field holds 1 of the 2 kinds of text that the package's docstring defines:

    | Field | Kind of text |
    |---|---|
    | `definitions` | LaTeX math on each side, with no ``$`` |
    | `expression` | LaTeX math, with no ``$`` |
    | `interval` | LaTeX math, with no ``$`` |
    | `summary` | a text for a reader, with its math as ``$…$`` inline and ``$$…$$`` for display |
    | `notes` | texts for a reader, with their math as ``$…$`` inline and ``$$…$$`` for display |

    Attributes:
        expression: The right side of ``f(x, c) = …``, as the formula's code computes it, including the conditions
            under which the code returns a fixed value. It may span several lines, such as a ``cases`` environment.
        interval: The interval that `Formula.interval_bounds` returns, in LaTeX, such as
            ``r"[-\param{b}, \param{b}]"``.
        definitions: The temporary variables and intermediate functions that the expression uses, in order, each as a
            pair of its left side and its right side, such as ``(r"\tmp{u}", r"\x - \c")`` or
            ``(r"\fn{g}(\x)", r"\sinh \x")``. A left side defines exactly 1 name, with 1 ``\tmp{…}`` or ``\fn{…}``
            marker. Empty by default.
        summary: Briefly, what the formula is, or what makes it an interesting test problem, such as "Oscillatory
            function with many roots". None by default; the catalog's tests require it of every shipped formula.
        notes: Paragraphs for a reader, such as a note that gives the original expression as display math when the
            formula's code computes an equivalent form of it. Empty by default.
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
        defined_names: list[tuple[str, str]] = []
        unused: set[tuple[str, str]] = set()
        for left_side, right_side in self.definitions:
            left_names = LatexTemplate(left_side).temporary_variables_and_functions
            if len(left_names) != 1:
                raise ValueError(
                    f"FormulaPresentation: the left side {left_side!r} must define exactly 1 name, with 1 "
                    "\\tmp{…} or \\fn{…} marker."
                )
            self._check_temporary_variables_and_functions_are_defined(
                LatexTemplate(right_side), defined_names, f"the definition of {left_side!r}"
            )
            unused -= set(LatexTemplate(right_side).temporary_variables_and_functions)
            if left_names[0] in defined_names:
                raise ValueError(f"FormulaPresentation: {left_side!r} defines a name that an earlier line defines.")
            defined_names.append(left_names[0])
            unused.add(left_names[0])
        for text in (self.expression, self.interval, *self.texts_for_a_reader):
            self._check_temporary_variables_and_functions_are_defined(
                LatexTemplate(text), defined_names, f"the text {text!r}"
            )
            unused -= set(LatexTemplate(text).temporary_variables_and_functions)
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
    def texts_for_a_reader(self) -> tuple[str, ...]:
        """Return the summary, where given, and the notes."""
        summary = (self.summary,) if self.summary is not None else ()
        return (*summary, *self.notes)

    @property
    def math_placeholder_names(self) -> frozenset[str]:
        r"""Return the names of the parameters whose placeholder appears in the fields of LaTeX math.

        A placeholder is ``\param{name}``; the fields of LaTeX math are `definitions`, `expression` and `interval`.
        """
        return frozenset(name for text in self._math_texts for name in LatexTemplate(text).placeholder_names)

    @property
    def placeholder_names(self) -> frozenset[str]:
        r"""Return the names of the parameters whose ``\param{…}`` placeholder appears in any field."""
        texts = (*self._math_texts, *self.texts_for_a_reader)
        return frozenset(name for text in texts for name in LatexTemplate(text).placeholder_names)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @property
    def _math_texts(self) -> tuple[str, ...]:
        """Return the fields that are LaTeX math: each side of each definition, `expression` and `interval`."""
        sides = [side for definition in self.definitions for side in definition]
        return (*sides, self.expression, self.interval)

    @staticmethod
    def _check_temporary_variables_and_functions_are_defined(
        template: LatexTemplate, defined_names: list[tuple[str, str]], where: str
    ) -> None:
        """Raise `ValueError` if `template` uses a temporary variable or function that `defined_names` does not hold."""
        undefined = [name for name in template.temporary_variables_and_functions if name not in defined_names]
        if undefined:
            raise ValueError(f"FormulaPresentation: {where} uses {undefined}, which no earlier definition defines.")
