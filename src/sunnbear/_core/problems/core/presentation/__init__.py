r"""This package holds what a reader sees of a formula: its math in LaTeX, and texts about it.

A formula declares a `FormulaPresentation`: its expression and its interval in LaTeX, the definitions of the temporary
variables and intermediate functions that the expression uses, a summary, notes and the conditions on its parameters.
Every one of them is written in sunnbear's LaTeX notation, described below. `LatexTemplate` holds 1 text in that
notation, checks it, and lists the parameters, temporary variables and intermediate functions that the text names.

`Formula` renders a text for a consumer, such as the website, in 1 of 2 forms:

- **with symbols** (`Formula.latex_with_symbols`): each placeholder becomes its parameter's `latex_symbol`;
- **with values** (`Formula.latex_with_values`): each placeholder becomes a test problem's value, spelled as the test
  problem's id spells it, with ``\cdot`` before a value that follows a number.

A text for a reader is always rendered with symbols. `Formula.latex_display` joins the definitions and
``f(\x, \c) = `` plus the expression into 1 aligned display, in either form.

A text is 1 of 2 kinds:

- **LaTeX math:** each side of a definition, the expression and the interval. The whole text is math, with no ``$``.
- **A text for a reader:** prose that marks its math as ``$…$`` inline and ``$$…$$`` for display, as mkdocs does. The
  texts for a reader are a presentation's summary, notes and parameter conditions, a parameter's meaning, a recipe's
  summary and a category's description.

The LaTeX of both kinds uses this notation:

- **a placeholder per parameter,** ``\param{name}``, which `Formula` replaces (`LatexTemplate.substitute`) before it
  hands the LaTeX out;
- **5 markers,** which stay in the LaTeX that `Formula` hands out, so that a consumer can style each kind of symbol:
  - ``\x``, the variable;
  - ``\c``, the parameter ``c``;
  - ``\tmp{…}``, a temporary variable, such as ``\tmp{u}`` or ``\tmp{t_1}``;
  - ``\fn{…}``, an intermediate function, such as ``\fn{g}(\x)``;
  - ``\prm{…}``, which wraps the symbol or the value that replaced a placeholder.

A consumer that renders the LaTeX defines each marker as a macro, such as one that colors its argument.
`PLAIN_MARKER_MACROS` holds plain definitions, in the form of the ``macros`` option of KaTeX, so that a consumer that
does not style the markers can still render the LaTeX.

``\c`` already exists in LaTeX as the cedilla accent, so the consumer's definition replaces it. A consumer that defines
no markers fails on ``\x``, which every formula's expression uses.
"""

from .formula_presentation import FormulaPresentation
from .latex_template import PLAIN_MARKER_MACROS, LatexTemplate
