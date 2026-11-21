r"""`LatexTemplate` holds 1 text in sunnbear's LaTeX notation, and owns that notation.

A formula's presentation writes its LaTeX, and the math in its texts, in this notation:

- **a placeholder per parameter,** ``\param{name}``, which `LatexTemplate.substitute` replaces before sunnbear hands
  the LaTeX out;
- **5 markers,** which stay in the LaTeX that sunnbear hands out, so that a consumer can style each role:
  - ``\x``, the variable;
  - ``\c``, the parameter ``c``;
  - ``\tmp{…}``, a temporary variable, such as ``\tmp{u}`` or ``\tmp{t_1}``;
  - ``\fn{…}``, an intermediate function, such as ``\fn{g}(\x)``;
  - ``\prm{…}``, which wraps the symbol or the value that replaced a placeholder.

A consumer that renders the LaTeX defines each marker as a macro. `DEFAULT_MARKER_MACROS` holds plain definitions,
in the form of the ``macros`` option of KaTeX, so that any consumer renders the LaTeX without styling it. ``\c`` is
LaTeX's cedilla accent, which the consumer's definition replaces; a consumer that defines no markers fails on ``\x``,
which every formula's expression uses.

A text for a reader marks its math as ``$…$`` inline and ``$$…$$`` for display, as mkdocs does.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar

# DEFAULT_MARKER_MACROS maps each marker to a plain definition, as KaTeX's `macros` option takes it: ``#1`` stands for
# the marker's argument.
DEFAULT_MARKER_MACROS = MappingProxyType(
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
    r"""`LatexTemplate` holds 1 text in sunnbear's LaTeX notation: LaTeX, or prose with LaTeX math.

    The argument of ``\tmp{…}`` and ``\fn{…}`` may hold 1 level of braces, as in ``\tmp{t_{1}}``.
    """

    text: str

    # a placeholder's name is the parameter's name, a Python identifier
    _PLACEHOLDER: ClassVar[re.Pattern[str]] = re.compile(r"\\param\{([A-Za-z_][A-Za-z0-9_]*)\}")
    _TEMPORARY_VARIABLE: ClassVar[re.Pattern[str]] = re.compile(r"\\tmp\{((?:[^{}]|\{[^{}]*\})+)\}")
    _INTERMEDIATE_FUNCTION: ClassVar[re.Pattern[str]] = re.compile(r"\\fn\{((?:[^{}]|\{[^{}]*\})+)\}")
    # a command of the notation, written in any way, so that a malformed one can be found
    _COMMAND: ClassVar[re.Pattern[str]] = re.compile(r"\\(param|tmp|fn)(?![A-Za-z])")

    def __post_init__(self) -> None:
        r"""Check that every ``\param``, ``\tmp`` and ``\fn`` in the text has a well-formed argument.

        Raises:
            ValueError: If a ``\param`` names no Python identifier, or a ``\tmp`` or ``\fn`` has no argument in braces.
        """
        well_formed = {
            "param": self._PLACEHOLDER,
            "tmp": self._TEMPORARY_VARIABLE,
            "fn": self._INTERMEDIATE_FUNCTION,
        }
        for command in self._COMMAND.finditer(self.text):
            if not well_formed[command[1]].match(self.text, command.start()):
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
        return self._names_in_order(self._PLACEHOLDER)

    @property
    def temporary_variable_names(self) -> tuple[str, ...]:
        r"""Return the arguments of the text's ``\tmp{…}`` markers, in the order of their first use."""
        return self._names_in_order(self._TEMPORARY_VARIABLE)

    @property
    def intermediate_function_names(self) -> tuple[str, ...]:
        r"""Return the arguments of the text's ``\fn{…}`` markers, in the order of their first use."""
        return self._names_in_order(self._INTERMEDIATE_FUNCTION)

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

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _names_in_order(self, pattern: re.Pattern[str]) -> tuple[str, ...]:
        """Return the distinct arguments that `pattern` matches in the text, in the order of their first match."""
        return tuple(dict.fromkeys(match[1] for match in pattern.finditer(self.text)))
