"""`XShiftedFormula` is the base class of a formula whose ``c`` shifts its function along x.

A subclass gives its function without ``c``, as ``unshifted_fun(x, p1, ...)``, and its interval as a static
``interval_bounds(p1, ...)`` that numba can compile. The class builds `parametrized_fun` from the 2::

    parametrized_fun(x, c, p1, ...) = unshifted_fun(x - (b - a)*c, p1, ...),   (a, b) = interval_bounds(p1, ...)

so ``c = 0`` gives the unshifted function exactly, and ``c`` moves it along x by ``c`` times the width of its
interval: a single root ``r`` stays inside ``[a, b]`` for ``c`` from ``(a - r)/(b - a)`` to ``(b - r)/(b - a)``, a
range of width 1 whatever the interval. The formulas of category 1, the published test functions, are
`XShiftedFormula` subclasses.
"""

import inspect
import keyword
from abc import abstractmethod
from collections.abc import Callable
from typing import cast

import numba

from .formula import Formula

# _PARAMETRIZED_FUN_TEMPLATE is the source of `parametrized_fun`; `{params}` takes the parameter names, each after
# a comma.
_PARAMETRIZED_FUN_TEMPLATE = """
def parametrized_fun(x, c{params}):
    lower, upper = _interval_bounds({args})
    return _unshifted_fun(x - (upper - lower) * c{params})
"""
# _TEMPLATE_NAMES are the names that the template uses besides the parameters, which a parameter may not take.
_TEMPLATE_NAMES = frozenset({"x", "c", "lower", "upper", "_interval_bounds", "_unshifted_fun"})


# ==================================================================================================
#  XShiftedFormula
# ==================================================================================================
class XShiftedFormula(Formula):
    """`XShiftedFormula` is a `Formula` whose ``c`` shifts its function along x, by ``c`` times its interval's width.

    A subclass implements `unshifted_fun` and a static `interval_bounds`, both named after `param_names`, and
    `recipes`; it does not implement `parametrized_fun`, which this class builds from the 2 hooks. With numba on,
    `parametrized_fun` compiles into 1 function, in which numba inlines both hooks.
    """

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Build `parametrized_fun` for a subclass that implements `unshifted_fun`, then validate it as `Formula` does.

        Raises:
            TypeError: If `interval_bounds` is not a ``@staticmethod``.
            ValueError: If a parameter name is not an identifier, or is a name that `parametrized_fun` uses.
        """
        if not getattr(cls.unshifted_fun, "__isabstractmethod__", False):
            if not isinstance(inspect.getattr_static(cls, "interval_bounds"), staticmethod):
                raise TypeError(
                    f"{cls.__name__}.interval_bounds must be a @staticmethod, because parametrized_fun calls it."
                )
            cls.parametrized_fun = staticmethod(cls._build_parametrized_fun(cls.unshifted_fun, cls.interval_bounds))
        super().__init_subclass__(**kwargs)

    # --------------------------------------------------------------------------
    #  Hooks implemented per formula
    # --------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def unshifted_fun(x: float, *params: float) -> float:
        """The formula's function without the shift, ``f(x, p1, p2, ...)``.

        Overrides must name their parameters, matching `param_names`, as for `Formula.parametrized_fun`.
        """

    # a static method where Formula has an instance method: calls through an instance still work alike
    @staticmethod
    @abstractmethod
    def interval_bounds(*params: float) -> tuple[float, float]:  # ty: ignore[invalid-method-override]
        """Return the interval ``(a, b)``, from which `parametrized_fun` takes the width of the shift.

        Unlike `Formula.interval_bounds`, the override is a ``@staticmethod`` that numba can compile, because
        `parametrized_fun` calls it. Overrides must name their parameters, matching `param_names`.
        """

    # --------------------------------------------------------------------------
    #  Framework-owned assembly
    # --------------------------------------------------------------------------
    @classmethod
    def _build_parametrized_fun(
        cls, unshifted_fun: Callable[..., float], interval_bounds: Callable[..., tuple[float, float]]
    ) -> Callable[..., float]:
        """Return `parametrized_fun`, generated with the class's parameter names, calling the 2 hooks given.

        The function is generated from source, so that it names its parameters as `Formula` requires of every
        `parametrized_fun`, and so that numba, which compiles no ``*params`` function with an explicit signature,
        can compile it.

        Raises:
            ValueError: If a parameter name is not an identifier, or is a name that the template uses.
        """
        for name in cls.param_names:
            if not name.isidentifier() or keyword.iskeyword(name) or name in _TEMPLATE_NAMES:
                raise ValueError(
                    f"{cls.__name__} declares the parameter {name!r}, which an XShiftedFormula cannot take: it is not "
                    f"an identifier, or it is 1 of {sorted(_TEMPLATE_NAMES)}."
                )
        source = _PARAMETRIZED_FUN_TEMPLATE.format(
            params="".join(f", {name}" for name in cls.param_names), args=", ".join(cls.param_names)
        )
        namespace: dict[str, object] = {"_interval_bounds": interval_bounds, "_unshifted_fun": unshifted_fun}
        exec(source, namespace)  # noqa: S102 - the source is the fixed template, with identifiers checked above
        return cast("Callable[..., float]", namespace["parametrized_fun"])

    @classmethod
    def _parametrized_fun_for_numba(cls) -> Callable[..., float]:
        """Return `parametrized_fun` built over numba-compiled forms of the 2 hooks, which numba inlines into it."""
        return cls._build_parametrized_fun(
            numba.njit(inline="always")(cls.unshifted_fun), numba.njit(inline="always")(cls.interval_bounds)
        )

    @classmethod
    def _hooks_with_param_tuple(cls) -> list[tuple[str, Callable[..., object], int]]:
        """Return the hooks of `Formula._hooks_with_param_tuple`, and `unshifted_fun`."""
        return [*super()._hooks_with_param_tuple(), ("unshifted_fun", cls.unshifted_fun, 1)]  # after x
