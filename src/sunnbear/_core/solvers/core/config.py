"""`SolverConfig` and `SolverConfigs` declare the configured solvers: a solver class, its init arguments, and a role.

A solver class carries only its algorithm; which settings the benchmark runs is a separate decision, recorded by
1 `SolverConfigs` subclass per solver class, which lists that solver's configs as `SolverConfig` values.

Defining the subclass registers each of its configs with `SolverConfigRegistry`, and every check runs at that moment,
so a malformed config fails when its module is imported, never inside a benchmark worker.
"""

import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar

from sunnbear._core.utils.class_origin import is_defined_in_sunnbear

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
    """`SolverConfig` describes one configured solver: its role, and the init arguments of its solver class.

    A config is declared in the ``configs`` of a `SolverConfigs` subclass, which sets ``solver_cls`` and
    ``module_name`` when it registers the config; a declaration gives only ``role`` and ``solver_kwargs``.

    Attributes:
        role: How the benchmark treats this config. A role for which `SolverRole.is_builtin_only` is true
            is reserved for configs declared inside the sunnbear package.
        solver_kwargs: The init arguments passed to ``solver_cls``; each value is a bool, int, float, or str, or a
            `StrEnum` member.
        solver_cls: The concrete `Solver` subclass to instantiate, the ``solver_cls`` of the declaring
            `SolverConfigs` subclass.
        module_name: The module of the declaring `SolverConfigs` subclass, which a benchmark worker imports to
            register the config in its own process.
    """

    role: SolverRole
    solver_kwargs: Mapping[str, object] = field(default_factory=dict)
    solver_cls: type[Solver] = field(init=False, repr=False)
    module_name: str = field(init=False, repr=False)

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

    # --------------------------------------------------------------------------
    #  Registration
    # --------------------------------------------------------------------------
    def declared_by(self, configs_cls: "type[SolverConfigs]") -> "SolverConfig":
        """Return a copy of this config with the solver class and the module of ``configs_cls``, its declaration.

        `SolverConfigs` calls this method on each of its configs before it registers them. ``solver_cls`` and
        ``module_name`` are not init arguments, so the copy sets them as a frozen dataclass sets a field outside
        ``__init__``.
        """
        config = SolverConfig(role=self.role, solver_kwargs=self.solver_kwargs)
        object.__setattr__(config, "solver_cls", configs_cls.solver_cls)
        object.__setattr__(config, "module_name", configs_cls.__module__)
        return config


# ==================================================================================================
#  SolverConfigs
# ==================================================================================================
class SolverConfigs:
    """`SolverConfigs` declares the configs of 1 solver class; a subclass lists them, and defining it registers them.

    Example::

        class TOMS748Configs(SolverConfigs):
            solver_cls = TOMS748
            configs = (
                SolverConfig(role=SolverRole.BUILTIN_CORE, solver_kwargs={"k": 2}),
                SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"k": 1}),
            )

    Class attributes:
        solver_cls: The concrete `Solver` subclass that every config of ``configs`` instantiates.
        configs: The solver's configs, at least 1.
    """

    solver_cls: ClassVar[type[Solver]]
    configs: ClassVar[tuple[SolverConfig, ...]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate the subclass and its configs, and register each config with `SolverConfigRegistry`.

        Raises:
            TypeError: If any of the following holds:

                - ``solver_cls`` or ``configs`` is missing
                - ``solver_cls`` is not a concrete `Solver` subclass
                - ``configs`` is not a non-empty tuple of `SolverConfig` values
                - a config's ``solver_kwargs`` do not fit ``solver_cls.__init__``, or a value has an unsupported
                  type
            ValueError: If a built-in-only role is used outside the sunnbear package, or registration
                fails (see `SolverConfigRegistry.register`).
        """
        super().__init_subclass__(**kwargs)
        cls._validate()
        # Every config is checked before any is registered, so a malformed declaration registers none of its configs.
        for config in cls.configs:
            cls._validate_config(config)
        for config in cls.configs:
            SolverConfigRegistry.register(config.declared_by(cls))

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @classmethod
    def _validate(cls) -> None:
        """Run every check that concerns this declaration alone; checks across configs run in the registry."""
        for attr in ("solver_cls", "configs"):
            if not hasattr(cls, attr):
                raise TypeError(f"{cls.__name__} must define {attr}.")
        if not (isinstance(cls.solver_cls, type) and issubclass(cls.solver_cls, Solver)):
            raise TypeError(f"{cls.__name__}.solver_cls must be a Solver subclass (got {cls.solver_cls!r}).")
        if inspect.isabstract(cls.solver_cls):
            raise TypeError(f"{cls.__name__}.solver_cls must be concrete; {cls.solver_cls.__name__} is abstract.")
        if not isinstance(cls.configs, tuple) or not cls.configs:
            raise TypeError(f"{cls.__name__}.configs must be a non-empty tuple of SolverConfig values.")

    @classmethod
    def _validate_config(cls, config: object) -> None:
        """Check that 1 entry of ``configs`` is a `SolverConfig` value that fits this declaration.

        Its role must be allowed where the subclass is defined, and its ``solver_kwargs`` must fit ``solver_cls``.
        """
        if not isinstance(config, SolverConfig):
            raise TypeError(f"{cls.__name__}.configs must hold only SolverConfig values (got {config!r}).")
        if config.role.is_builtin_only and not is_defined_in_sunnbear(cls):
            raise ValueError(
                f"{cls.__name__} is defined in {cls.__module__}, but role {config.role.name} is reserved for "
                "configs inside the sunnbear package; use SolverRole.USER_ACTIVE or SolverRole.USER_OTHER."
            )
        try:
            inspect.signature(cls.solver_cls).bind(**config.solver_kwargs)
        except TypeError as exc:
            raise TypeError(
                f"{cls.__name__}: solver_kwargs do not fit {cls.solver_cls.__name__}.__init__: {exc}."
            ) from exc
        for key, value in config.solver_kwargs.items():
            if not isinstance(value, _SOLVER_KWARG_VALUE_TYPES):
                raise TypeError(
                    f"{cls.__name__}: solver_kwargs[{key!r}] must be a bool, int, float, or str "
                    f"(got {type(value).__name__})."
                )
