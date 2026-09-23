"""Stable identity of a test function: formula number plus its named, bound parameter tuple.

A `FunctionId` holds the formula number, the formula's parameter names, and the
parameter values — nothing else. In particular there is no materialization-order
counter: which recipe produced a parameter tuple, or in which order, never affects
identity, so identities are stable under recipe edits and reordering.

The rendering names each parameter, e.g. ``f2.1.5[p1=2^1.2,p2=0.4]``, in the formula's
declared parameter order, so a reader can tell the values apart without looking up the
formula, and `from_string` parses it without consulting the registry. A formula without
parameters renders as its number alone, e.g. ``f7.1``.

Identities inherit the faithfulness of their parameter values (see
`param_values`): there is a single rendering, notation-carrying and parsed
back losslessly by `from_string`. Equality, hashing, and ordering are exact —
two ids match when they carry the same formula, the same parameter names, and the
same parameter values in the same notation; collapsing near-duplicate parameter
tuples happens *before* identities are built (`deduplicate_param_tuples`).
"""

import re
from dataclasses import dataclass

from .param_values import ParamValue
from .taxonomy import FormulaTaxonomyNode

# A rendered identity is ``f`` + a dotted number, then optionally ``[name=value,...]``.
_FUNCTION_ID_PATTERN = re.compile(r"f(?P<number>[0-9.]+)(?:\[(?P<params>[^\[\]]+)\])?")


# ==================================================================================================
#  FunctionId
# ==================================================================================================
@dataclass(frozen=True)
class FunctionId:
    """Identity of one test function: formula number + the named, bound parameter tuple.

    Equality and hashing are the dataclass defaults — exact, and notation-aware,
    since the parameter values carry their notation. Rendering is faithful and
    re-parseable (see the module docstring).

    Attributes:
        formula_number: The formula's taxonomy number, e.g. ``(2, 1, 1)``.
        param_names: The formula's declared parameter names, in the order it binds them.
        params: One value per name in `param_names`, in the same order.
    """

    formula_number: tuple[int, ...]
    param_names: tuple[str, ...]
    params: tuple[ParamValue, ...]

    def __post_init__(self) -> None:
        """Check that every parameter value has a name.

        Raises:
            ValueError: If `param_names` and `params` differ in length.
        """
        if len(self.param_names) != len(self.params):
            raise ValueError(
                f"FunctionId has {len(self.param_names)} parameter name(s) but {len(self.params)} value(s)."
            )

    @property
    def param_values(self) -> tuple[float, ...]:
        """Return the plain float values, e.g. for handing to formula code."""
        return tuple(p.value for p in self.params)

    def __lt__(self, other: "FunctionId") -> bool:
        """Order by formula number, then parameter values."""
        return (self.formula_number, self.param_values) < (other.formula_number, other.param_values)

    # --------------------------------------------------------------------------
    #  Rendering
    # --------------------------------------------------------------------------
    def display(self) -> str:
        """Render with each parameter's name and authored notation, e.g. ``f2.1.5[p1=2^1.2,p2=0.4]``."""
        prefix = f"f{FormulaTaxonomyNode.format_number(self.formula_number)}"
        if not self.params:
            return prefix
        else:
            args = ",".join(
                f"{name}={value.display()}" for name, value in zip(self.param_names, self.params, strict=True)
            )
            return f"{prefix}[{args}]"

    def __repr__(self) -> str:
        """Render the faithful form; `from_string` parses it back to this identity."""
        return self.display()

    def __str__(self) -> str:
        """Same as `__repr__` — there is one rendering, so both agree."""
        return repr(self)

    @classmethod
    def from_string(cls, text: str) -> "FunctionId":
        """Parse a rendered identity back into a `FunctionId`.

        Raises:
            ValueError: If `text` does not follow the rendered form.
        """
        match = _FUNCTION_ID_PATTERN.fullmatch(text)
        if match is None:
            raise ValueError(f"Invalid FunctionId string: {text!r}")
        try:
            formula_number = FormulaTaxonomyNode.parse_number(match["number"])
            param_names, params = cls._parse_named_params(match["params"]) if match["params"] else ((), ())
        except ValueError as exc:
            raise ValueError(f"Invalid FunctionId string: {text!r}") from exc
        return cls(formula_number=formula_number, param_names=param_names, params=params)

    @staticmethod
    def _parse_named_params(text: str) -> tuple[tuple[str, ...], tuple[ParamValue, ...]]:
        """Parse ``name=value,name=value`` into the parameter names and their values, in order.

        Raises:
            ValueError: If an argument is not ``name=value`` with a valid identifier as name, or a
                name repeats.
        """
        names: list[str] = []
        values: list[ParamValue] = []
        for arg in text.split(","):
            name, equals, token = arg.partition("=")
            if not equals or not name.isidentifier():
                raise ValueError(f"Invalid parameter argument: {arg!r}")
            names.append(name)
            values.append(ParamValue.parse(token))
        if len(set(names)) != len(names):
            raise ValueError(f"Repeated parameter name in {text!r}")
        return tuple(names), tuple(values)
