"""`SolverConfig` is the base class of a solver configuration: it names a solver class, its init arguments, and a role.

A solver class carries only its algorithm; which settings the benchmark runs is a separate decision,
recorded by one `SolverConfig` subclass per setting.

Defining the subclass registers it with `SolverConfigRegistry`, and every check runs at that moment,
so a malformed config fails when its module is imported, never inside a benchmark worker.
"""

import inspect
from collections.abc import Mapping
from typing import ClassVar

from .registry import SolverConfigRegistry
from .role import SolverRole
from .solver import Solver

# A config's identity (`SolverConfig.solver_id`) is rebuilt in other processes, so each init argument must
# print the same everywhere.
_KWARG_VALUE_TYPES = (bool, int, float, str)


# ==================================================================================================
#  SolverConfig
# ==================================================================================================
class SolverConfig:
    """`SolverConfig` describes one configured solver; a subclass declares it, and defining the subclass registers it.

    Example::

        class RegulaFalsiConfig(SolverConfig):
            solver_cls = RegulaFalsi
            role = SolverRole.BUILTIN_SECONDARY

    Class attributes:
        solver_cls: The concrete `Solver` subclass to instantiate.
        kwargs: The init arguments passed to ``solver_cls``; each value is a bool, int, float, or str.
        role: How the benchmark treats this config. A role for which `SolverRole.is_builtin_only`
            holds is reserved for configs defined inside the sunnbear package.
    """

    solver_cls: ClassVar[type[Solver]]
    kwargs: ClassVar[Mapping[str, object]] = {}
    role: ClassVar[SolverRole]

    def __init_subclass__(cls, **subclass_kwargs: object) -> None:
        """Validate the subclass and register it with `SolverConfigRegistry`.

        Raises:
            TypeError: If any of the following holds:

                - ``solver_cls`` or ``role`` is missing
                - ``solver_cls`` is not a concrete `Solver` subclass
                - ``kwargs`` do not fit its ``__init__``
                - a ``kwargs`` value has an unsupported type
            ValueError: If a built-in-only role is used outside the sunnbear package, or registration
                fails (see `SolverConfigRegistry.register`).
        """
        super().__init_subclass__(**subclass_kwargs)
        cls._validate()
        SolverConfigRegistry.register(cls)

    # --------------------------------------------------------------------------
    #  Identity and construction
    # --------------------------------------------------------------------------
    @property
    def solver_id(self) -> str:
        """Return the config's identity, the solver's name plus its init arguments, e.g. ``itp[n_slack=4]``.

        Arguments are sorted by name, so the identity does not depend on the order of declaration.
        """
        if not self.kwargs:
            return self.solver_cls.name
        else:
            args = ",".join(f"{key}={value!r}" for key, value in sorted(self.kwargs.items()))
            return f"{self.solver_cls.name}[{args}]"

    def instantiate(self) -> Solver:
        """Return a new solver built with this config's init arguments."""
        return self.solver_cls(**self.kwargs)

    # --------------------------------------------------------------------------
    #  Validation
    # --------------------------------------------------------------------------
    @classmethod
    def _validate(cls) -> None:
        """Run every check that concerns this config alone; checks across configs run in the registry."""
        for attr in ("solver_cls", "role"):
            if not hasattr(cls, attr):
                raise TypeError(f"{cls.__name__} must define {attr}.")
        if not (isinstance(cls.solver_cls, type) and issubclass(cls.solver_cls, Solver)):
            raise TypeError(f"{cls.__name__}.solver_cls must be a Solver subclass (got {cls.solver_cls!r}).")
        if inspect.isabstract(cls.solver_cls):
            raise TypeError(f"{cls.__name__}.solver_cls must be concrete; {cls.solver_cls.__name__} is abstract.")
        try:
            inspect.signature(cls.solver_cls).bind(**cls.kwargs)
        except TypeError as exc:
            raise TypeError(f"{cls.__name__}.kwargs do not fit {cls.solver_cls.__name__}.__init__: {exc}.") from exc
        for key, value in cls.kwargs.items():
            if not isinstance(value, _KWARG_VALUE_TYPES):
                raise TypeError(
                    f"{cls.__name__}.kwargs[{key!r}] must be a bool, int, float, or str (got {type(value).__name__})."
                )
        if cls.role.is_builtin_only and not _is_defined_in_sunnbear(cls):
            raise ValueError(
                f"{cls.__name__} is defined in {cls.__module__}, but role {cls.role.name} is reserved for "
                "configs inside the sunnbear package; use SolverRole.USER_ACTIVE or SolverRole.USER_OTHER."
            )


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _is_defined_in_sunnbear(cls: type) -> bool:
    """Return whether ``cls`` is defined in a module of the sunnbear package."""
    return cls.__module__ == "sunnbear" or cls.__module__.startswith("sunnbear.")
