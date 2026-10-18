"""The solver config registry holds the registered solver configs and looks one up by its identity.

Defining a `SolverConfigs` subclass registers each of its configs here. The built-in configs are
registered when the `sunnbear.solvers` module imports the shipped solvers, so the registry is complete
on import.

A benchmark worker receives a ``solver_id`` and rebuilds the solver as
``SolverConfigRegistry.config_from_id(solver_id).instantiate()``.
"""

from typing import TYPE_CHECKING, ClassVar

from .exceptions import UnknownSolverConfigError
from .role import SolverRole

if TYPE_CHECKING:  # type-only: config imports this module at runtime, so a runtime import here would be circular
    from .config import SolverConfig
    from .solver import Solver


# ==================================================================================================
#  SolverConfigRegistry
# ==================================================================================================
class SolverConfigRegistry:
    """`SolverConfigRegistry` enumerates the registered solver configs, or looks one up by ``solver_id``.

    `SolverConfigs.__init_subclass__` calls `register` for every config of every subclass; nothing is discovered
    lazily.
    """

    _configs_by_id: ClassVar[dict[str, "SolverConfig"]] = {}

    @classmethod
    def register(cls, config: "SolverConfig") -> None:
        """Register a config under its ``solver_id``.

        Raises:
            ValueError: If another registered config has the same ``solver_id``, or the config is a
                second one with role ``BUILTIN_BASELINE``.
        """
        if config.solver_id in cls._configs_by_id:
            existing_module_name = cls._configs_by_id[config.solver_id].module_name
            raise ValueError(
                f"Duplicate solver_id {config.solver_id!r}: declared in {config.module_name} and in "
                f"{existing_module_name}."
            )
        baseline = next((c for c in cls._configs_by_id.values() if c.role is SolverRole.BUILTIN_BASELINE), None)
        if config.role is SolverRole.BUILTIN_BASELINE and baseline is not None:
            raise ValueError(
                f"Only one config may have role BUILTIN_BASELINE: {config.solver_id} and {baseline.solver_id}."
            )
        cls._configs_by_id[config.solver_id] = config

    @classmethod
    def configs(cls) -> "tuple[SolverConfig, ...]":
        """Return every registered config, sorted by ``solver_id``."""
        return tuple(config for _, config in sorted(cls._configs_by_id.items()))

    @classmethod
    def solver_classes(cls) -> "tuple[type[Solver], ...]":
        """Return the solver class of every registered config, once each, in the order of `configs`."""
        return tuple(dict.fromkeys(config.solver_cls for config in cls.configs()))

    @classmethod
    def config_from_id(cls, solver_id: str) -> "SolverConfig":
        """Return the registered config with this ``solver_id``.

        Raises:
            UnknownSolverConfigError: If no registered config has this ``solver_id``.
        """
        config = cls._configs_by_id.get(solver_id)
        if config is None:
            raise UnknownSolverConfigError(f"No registered solver config with solver_id {solver_id!r}.")
        return config
