r"""`FormulaPresentation` holds what a reader sees of a formula: its expression and interval in LaTeX, and its texts.

Every field is written in sunnbear's LaTeX notation, which `latex_template` describes: ``\param{name}`` for a
parameter, and the markers ``\x``, ``\c``, ``\tmp{…}`` and ``\fn{…}``. `Formula` renders the fields with its parameters'
symbols, or with a test problem's values.
"""

from dataclasses import dataclass

from .latex_template import LatexTemplate


# ==================================================================================================
#  FormulaPresentation
# ==================================================================================================
@dataclass(frozen=True)
class FormulaPresentation:
    r"""`FormulaPresentation` holds a formula's expression and interval in LaTeX, and its texts for a reader.

    An expression over several lines is a list of definitions plus the expression. `Formula` joins them into 1 aligned
    display, so no field writes the layout's ``\\`` or ``&``.

    Attributes:
        expression: The right side of ``f(x, c) = …``, as the formula's code computes it, guards included. It may span
            several lines, such as a ``cases`` environment.
        interval: The interval, such as ``r"[-\param{b}, \param{b}]"``.
        definitions: Optional: the temporary variables and intermediate functions that the expression uses, in order,
            each as a pair of its left side and its right side, such as ``(r"\tmp{u}", r"\x - \c")`` or
            ``(r"\fn{g}(\x)", r"\sinh \x")``. A left side defines exactly 1 name, with 1 ``\tmp{…}`` or ``\fn{…}``
            marker.
        summary: Optional here: briefly, what the formula is, or what makes it an interesting test problem, such as
            "Oscillatory function with many roots". The catalog's tests require it of every shipped formula.
        notes: Optional paragraphs for a reader, such as the expression that the formula models where its code computes
            another form.
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
            left_names = self._marked_names(LatexTemplate(left_side))
            if len(left_names) != 1:
                raise ValueError(
                    f"FormulaPresentation: the left side {left_side!r} must define exactly 1 name, with 1 "
                    "\\tmp{…} or \\fn{…} marker."
                )
            self._check_names_are_defined(LatexTemplate(right_side), defined, f"the definition of {left_side!r}")
            unused -= set(self._marked_names(LatexTemplate(right_side)))
            if left_names[0] in defined:
                raise ValueError(f"FormulaPresentation: {left_side!r} defines a name that an earlier line defines.")
            defined.append(left_names[0])
            unused.add(left_names[0])
        for text in self._texts_after_the_definitions():
            self._check_names_are_defined(LatexTemplate(text), defined, f"the text {text!r}")
            unused -= set(self._marked_names(LatexTemplate(text)))
        if unused:
            raise ValueError(f"FormulaPresentation: the definitions of {sorted(unused)} are never used.")

    # --------------------------------------------------------------------------
    #  Templates
    # --------------------------------------------------------------------------
    @property
    def templates(self) -> tuple[LatexTemplate, ...]:
        """Return every field as a `LatexTemplate`: each side of each definition, the expression and the other texts."""
        sides = [side for definition in self.definitions for side in definition]
        return tuple(LatexTemplate(text) for text in (*sides, *self._texts_after_the_definitions()))

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _texts_after_the_definitions(self) -> tuple[str, ...]:
        """Return the expression, the interval, and the summary and notes where given."""
        summary = (self.summary,) if self.summary is not None else ()
        return (self.expression, self.interval, *summary, *self.notes)

    @staticmethod
    def _marked_names(template: LatexTemplate) -> tuple[tuple[str, str], ...]:
        r"""Return the temporary variables and intermediate functions that `template` marks, as pairs of kind and name.

        The kind keeps a temporary variable ``\tmp{g}`` apart from an intermediate function ``\fn{g}``.
        """
        return (
            *(("tmp", name) for name in template.temporary_variable_names),
            *(("fn", name) for name in template.intermediate_function_names),
        )

    @classmethod
    def _check_names_are_defined(cls, template: LatexTemplate, defined: list[tuple[str, str]], where: str) -> None:
        """Raise `ValueError` if `template` uses a temporary variable or function that `defined` does not hold."""
        undefined = [name for name in cls._marked_names(template) if name not in defined]
        if undefined:
            raise ValueError(f"FormulaPresentation: {where} uses {undefined}, which no earlier definition defines.")
