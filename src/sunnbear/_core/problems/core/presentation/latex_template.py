"""`LatexTemplate` holds 1 text in sunnbear's LaTeX notation, which the package's docstring describes."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar

# ``#1`` stands for the marker's argument, as in KaTeX's `macros` option.
PLAIN_MARKER_MACROS = MappingProxyType(
    {
        r"\x": "x",
        r"\c": "c",
        r"\tmp": "#1",
        r"\fn": "#1",
        r"\prm": "#1",
    }
)


# ==================================================================================================
#  LatexTemplate
# ==================================================================================================
@dataclass(frozen=True)
class LatexTemplate:
    r"""`LatexTemplate` holds 1 text in sunnbear's LaTeX notation: LaTeX, or a text for a reader with LaTeX math.

    The argument of ``\tmp{…}`` and ``\fn{…}`` may hold 1 level of braces, as in ``\tmp{t_{1}}``.
    """

    text: str

    # a placeholder's name is the parameter's name, a Python identifier
    _PLACEHOLDER: ClassVar[re.Pattern[str]] = re.compile(r"\\param\{([A-Za-z_][A-Za-z0-9_]*)\}")
    # _MARKER_ARGUMENT is a marker's argument in braces, which may hold 1 level of braces.
    _MARKER_ARGUMENT: ClassVar[str] = r"\{((?:[^{}]|\{[^{}]*\})+)\}"
    _TEMPORARY_VARIABLE: ClassVar[re.Pattern[str]] = re.compile(r"\\tmp" + _MARKER_ARGUMENT)
    _INTERMEDIATE_FUNCTION: ClassVar[re.Pattern[str]] = re.compile(r"\\fn" + _MARKER_ARGUMENT)
    # _ARGUMENT_PATTERN_BY_COMMAND holds, for each command with an argument, the pattern of the command with a
    # well-formed argument.
    _ARGUMENT_PATTERN_BY_COMMAND: ClassVar[Mapping[str, re.Pattern[str]]] = MappingProxyType(
        {"param": _PLACEHOLDER, "tmp": _TEMPORARY_VARIABLE, "fn": _INTERMEDIATE_FUNCTION}
    )
    # _COMMAND_WITH_ARGUMENT matches each command of _ARGUMENT_PATTERN_BY_COMMAND, whatever argument follows it, so that
    # __post_init__ finds a malformed one; a longer command such as ``\fnsymbol`` does not match.
    _COMMAND_WITH_ARGUMENT: ClassVar[re.Pattern[str]] = re.compile(
        r"\\(" + "|".join(_ARGUMENT_PATTERN_BY_COMMAND) + r")(?![A-Za-z])"
    )
    # _NUMBER_OR_EXPONENT_AT_END matches a text that ends, before any trailing spaces, in 1 of 3 things: a digit that is
    # not a subscript, a placeholder, or an exponent in braces.
    _NUMBER_OR_EXPONENT_AT_END: ClassVar[re.Pattern[str]] = re.compile(
        r"(?:(?<!_)\d|" + _PLACEHOLDER.pattern + r"|\^\{[^{}]*\})\s*$"
    )

    def __post_init__(self) -> None:
        r"""Check that every ``\param``, ``\tmp`` and ``\fn`` in the text has a well-formed argument.

        Raises:
            ValueError: If a ``\param`` names no Python identifier, or a ``\tmp`` or ``\fn`` has no argument in braces.
        """
        for command in self._COMMAND_WITH_ARGUMENT.finditer(self.text):
            if not self._ARGUMENT_PATTERN_BY_COMMAND[command[1]].match(self.text, command.start()):
                raise ValueError(
                    f"LatexTemplate: \\{command[1]} at position {command.start()} has no well-formed argument in "
                    f"{self.text!r}."
                )

    # --------------------------------------------------------------------------
    #  Names in the text
    # --------------------------------------------------------------------------
    @property
    def placeholder_names(self) -> tuple[str, ...]:
        """Return the parameter names of the text's placeholders, in the order of their first use."""
        return tuple(dict.fromkeys(match[1] for match in self._PLACEHOLDER.finditer(self.text)))

    @property
    def temporary_variables_and_functions(self) -> tuple[tuple[str, str], ...]:
        r"""Return the text's temporary variables and intermediate functions, as pairs of marker and name.

        Each pair appears once, in the order of its first use, temporary variables first. The marker keeps a temporary
        variable ``\tmp{g}`` apart from an intermediate function ``\fn{g}``.
        """
        return tuple(
            dict.fromkeys(
                [("tmp", match[1]) for match in self._TEMPORARY_VARIABLE.finditer(self.text)]
                + [("fn", match[1]) for match in self._INTERMEDIATE_FUNCTION.finditer(self.text)]
            )
        )

    # --------------------------------------------------------------------------
    #  Substitution
    # --------------------------------------------------------------------------
    def substitute(self, latex_by_name: Mapping[str, str]) -> str:
        r"""Return the text with each placeholder replaced by the LaTeX for its name, wrapped in ``\prm{…}``.

        Args:
            latex_by_name: The LaTeX for each parameter name, such as its symbol or its value; it may hold names that
                the text does not use.

        Raises:
            ValueError: If the text has a placeholder whose name `latex_by_name` does not hold.
        """
        missing = [name for name in self.placeholder_names if name not in latex_by_name]
        if missing:
            raise ValueError(f"LatexTemplate: no LaTeX for the placeholders {missing} of {self.text!r}.")
        else:
            return self._PLACEHOLDER.sub(lambda match: rf"\prm{{{latex_by_name[match[1]]}}}", self.text)

    def substitute_values(self, latex_by_name: Mapping[str, str]) -> str:
        r"""Return the text as `substitute` returns it, with ``\cdot`` before each value that follows a number.

        ``\cdot`` goes before each value that follows 1 of these, because the value would otherwise read as part of the
        number before it:

        - a digit outside a subscript;
        - another value;
        - an exponent in braces.

        For example, ``1.54226 \param{w}`` at ``w = 0.2`` would render as 1.542260.2, and ``2 \param{n}`` at ``n = 4``
        as 24.

        A symbol needs no dot, because ``2 \param{n}`` with the symbol ``n`` reads as ``2n``.

        Args:
            latex_by_name: The LaTeX of each parameter's value, such as ``"0.2"``; it may hold names that the text does
                not use.

        Raises:
            ValueError: If the text has a placeholder whose name `latex_by_name` does not hold.
        """

        def placeholder_with_dot_where_needed(match: re.Match[str]) -> str:
            r"""Return the placeholder of `match`, with ``\cdot`` before it where a number precedes it."""
            if self._NUMBER_OR_EXPONENT_AT_END.search(self.text, 0, match.start()):
                return rf"\cdot {match[0]}"
            else:
                return match[0]

        text_with_dots = self._PLACEHOLDER.sub(placeholder_with_dot_where_needed, self.text)
        return LatexTemplate(text_with_dots).substitute(latex_by_name)
