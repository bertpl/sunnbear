r"""`LatexTemplate` holds 1 text in sunnbear's LaTeX notation, and defines that notation.

The LaTeX of a formula's presentation, and the math in the texts for a reader that the last paragraph lists, use this
notation:

- **a placeholder per parameter,** ``\param{name}``, which `LatexTemplate.substitute` replaces before sunnbear hands
  the LaTeX out;
- **5 markers,** which stay in the LaTeX that sunnbear hands out, so that a consumer can style each kind of symbol:
  - ``\x``, the variable;
  - ``\c``, the parameter ``c``;
  - ``\tmp{…}``, a temporary variable, such as ``\tmp{u}`` or ``\tmp{t_1}``;
  - ``\fn{…}``, an intermediate function, such as ``\fn{g}(\x)``;
  - ``\prm{…}``, which wraps the symbol or the value that replaced a placeholder.

A consumer that renders the LaTeX defines each marker as a macro. `PLAIN_MARKER_MACROS` holds plain definitions, in the
form of the ``macros`` option of KaTeX, so that a consumer that does not style the markers can still render the LaTeX.

``\c`` already exists in LaTeX as the cedilla accent, so the consumer's definition replaces it. A consumer that defines
no markers fails on ``\x``, which every formula's expression uses.

A text for a reader marks its math as ``$…$`` inline and ``$$…$$`` for display, as mkdocs does. The texts for a reader
are:

- a presentation's summary and notes;
- a parameter's meaning;
- a recipe's summary;
- a category's description.
"""

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
