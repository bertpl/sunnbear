"""`SolverConfig` and `SolverConfigsDeclaration` declare the configured solvers.

A config names a solver class, its init arguments, and a role.

A solver class carries only its algorithm; which settings the benchmark runs is a separate decision, recorded by
`SolverConfigsDeclaration` subclasses, which list the configs as `SolverConfig` values. Each built-in solver package has
1 such subclass, which declares the configs of every solver class in the package.

Defining the subclass registers each of its configs with `SolverConfigRegistry`, and every check has run by that
moment, so a malformed config fails when its module is imported, never inside a benchmark worker.
"""

import dataclasses
import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from sunnbear._core.utils.class_origin import is_sunnbear_module

from .registry import SolverConfigRegistry
from .role import SolverRole
from .solver import Solver

# The types that a `solver_kwargs` value may have. `SolverConfig.solver_id` includes the `repr` of each
# value, and a worker in another process must rebuild the same id, which holds for these types only. An enum
# member of one of these types, such as a `StrEnum` member, counts as its type; the id shows its plain value.
_SOLVER_KWARG_VALUE_TYPES = (bool, int, float, str)


# ==================================================================================================
#  SolverConfig
# ==================================================================================================
@dataclass(frozen=True, kw_only=True, eq=False)
class SolverConfig:
    """`SolverConfig` describes one configured solver: its solver class, that class's init arguments, and a role.

    A config is declared in the ``configs`` of a `SolverConfigsDeclaration` subclass. Defining that subclass registers a
    copy of each config, with ``declaring_module_name`` set.

    Attributes:
        solver_cls: The concrete `Solver` subclass to instantiate.
        role: How the benchmark treats this config. A role for which `SolverRole.is_builtin_only` is true
            is reserved for configs declared inside the sunnbear package.
        solver_kwargs: The init arguments passed to ``solver_cls``; each value is a bool, int, float, or str, or a
            `StrEnum` member.
        declaring_module_name: The module of the declaring `SolverConfigsDeclaration` subclass, which a benchmark worker
            imports to register the config in its own process.
    """

    # Solver[Any], because each solver class fixes its own state type; a bare Solver means Solver[SolveState].
    solver_cls: type[Solver[Any]]
    role: SolverRole
    solver_kwargs: Mapping[str, object] = field(default_factory=dict)
    declaring_module_name: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Check that ``solver_cls`` is a concrete `Solver` subclass, and that ``solver_kwargs`` fit its ``__init__``.

        Each ``solver_kwargs`` value must also have a type that `solver_id` can write as text.

        Raises:
            TypeError: If ``solver_cls`` is not a concrete `Solver` subclass, if a ``solver_kwargs`` value is not a
                bool, int, float, or str, or if ``solver_kwargs`` do not fit ``solver_cls.__init__``.
        """
        if not (isinstance(self.solver_cls, type) and issubclass(self.solver_cls, Solver)):
            raise TypeError(f"SolverConfig: solver_cls must be a Solver subclass (got {self.solver_cls!r}).")
        if inspect.isabstract(self.solver_cls):
            raise TypeError(f"SolverConfig: solver_cls must be concrete; {self.solver_cls.__name__} is abstract.")
        for key, value in self.solver_kwargs.items():
            if not isinstance(value, _SOLVER_KWARG_VALUE_TYPES):
                raise TypeError(
                    f"SolverConfig: solver_kwargs[{key!r}] must be a bool, int, float, or str "
                    f"(got {type(value).__name__})."
                )
        try:
            inspect.signature(self.solver_cls).bind(**self.solver_kwargs)
        except TypeError as exc:
            raise TypeError(
                f"SolverConfig: solver_kwargs do not fit {self.solver_cls.__name__}.__init__: {exc}."
            ) from exc

    # --------------------------------------------------------------------------
    #  Identity and construction
    # --------------------------------------------------------------------------
    @property
    def solver_id(self) -> str:
        """Return the config's identity, the solver's name plus its init arguments, e.g. ``toms748[k=1]``.

        Arguments are sorted by name, so the identity does not depend on the order of declaration.
        """
        if not self.solver_kwargs:
            return self.solver_cls.name
        else:
            # An enum member shows as its plain value, e.g. 'scipy', not as <RiddersVariant.SCIPY: 'scipy'>.
            values = {
                key: value.value if isinstance(value, Enum) else value for key, value in self.solver_kwargs.items()
            }
            args = ",".join(f"{key}={value!r}" for key, value in sorted(values.items()))
            return f"{self.solver_cls.name}[{args}]"

    def instantiate(self) -> Solver:
        """Return a new solver built with this config's init arguments."""
        return self.solver_cls(**self.solver_kwargs)


# ==================================================================================================
#  SolverConfigsDeclaration
# ==================================================================================================
class SolverConfigsDeclaration:
    """`SolverConfigsDeclaration` is the base class that declares solver configs, of 1 or more solver classes.

    A subclass lists the configs, and defining the subclass registers them. Each config names its own solver class, so
    1 subclass can declare the configs of several solver classes.

    Example::

        class TOMS748ConfigsDeclaration(SolverConfigsDeclaration):
            configs = (
                SolverConfig(solver_cls=TOMS748, role=SolverRole.BUILTIN_CORE, solver_kwargs={"k": 2}),
                SolverConfig(solver_cls=TOMS748, role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"k": 1}),
            )

    Class attributes:
        configs: The declared configs, at least 1.
    """

    configs: ClassVar[tuple[SolverConfig, ...]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate the subclass and its configs, and register each config with `SolverConfigRegistry`.

        `SolverConfig` checks each config's solver class and init arguments when the config is built; this method
        checks what depends on the subclass.

        Raises:
            TypeError: If ``configs`` is missing, or is not a non-empty tuple of `SolverConfig` values.
            ValueError: If a built-in-only role is used outside the sunnbear package, or registration
                fails (see `SolverConfigRegistry.register`).
        """
        super().__init_subclass__(**kwargs)
        cls._validate_configs()
        # declaring_module_name is not an init argument, so the loop sets it on each registered copy with
        # object.__setattr__, which can set a field of a frozen dataclass outside __init__.
        for config in cls.configs:
            config_copy = dataclasses.replace(config)
            object.__setattr__(config_copy, "declaring_module_name", cls.__module__)
            SolverConfigRegistry.register(config_copy)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @classmethod
    def _validate_configs(cls) -> None:
        """Check ``configs``, and that this subclass may declare each of them.

        Every config is checked before any is registered, so a subclass with 1 malformed config registers none of its
        configs; the registry checks across configs.
        """
        if not hasattr(cls, "configs"):
            raise TypeError(f"{cls.__name__} must define configs.")
        if not isinstance(cls.configs, tuple) or not cls.configs:
            raise TypeError(f"{cls.__name__}.configs must be a non-empty tuple of SolverConfig values.")
        for config in cls.configs:
            if not isinstance(config, SolverConfig):
                raise TypeError(f"{cls.__name__}.configs must hold only SolverConfig values (got {config!r}).")
            if config.role.is_builtin_only and not is_sunnbear_module(cls.__module__):
                raise ValueError(
                    f"{cls.__name__} is defined in {cls.__module__}, but role {config.role.name} is reserved for "
                    "configs inside the sunnbear package; use SolverRole.USER_ACTIVE or SolverRole.USER_OTHER."
                )
