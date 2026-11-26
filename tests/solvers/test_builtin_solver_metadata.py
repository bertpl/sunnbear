"""These tests assert that every built-in solver states a readable name and whether it brackets, and that every
built-in config states a readable name and a summary."""

import pytest

from sunnbear._core.utils.class_origin import is_sunnbear_module
from sunnbear.solvers import SolverConfigRegistry

_BUILTIN_CONFIGS = [config for config in SolverConfigRegistry.configs() if config.role.is_builtin_only]
_BUILTIN_SOLVER_CLASSES = [
    solver_cls for solver_cls in SolverConfigRegistry.solver_classes() if is_sunnbear_module(solver_cls.__module__)
]


@pytest.mark.parametrize("solver_cls", _BUILTIN_SOLVER_CLASSES, ids=lambda solver_cls: solver_cls.__name__)
def test_a_builtin_solver_has_a_readable_name_and_brackets_exactly_in_the_bracketing_package(solver_cls):
    """A built-in solver has a readable name, and the solver is bracketing exactly when its class lives in the
    package of the bracketing solvers."""
    # --- act / assert -----------------
    assert solver_cls.readable_name
    assert solver_cls.is_bracketing is solver_cls.__module__.startswith("sunnbear._core.solvers.bracketing.")


@pytest.mark.parametrize("config", _BUILTIN_CONFIGS, ids=lambda config: config.solver_id)
def test_a_builtin_config_has_a_readable_name_and_a_summary(config):
    """A built-in config has a readable name and a summary that is not empty."""
    # --- act / assert -----------------
    assert config.readable_name
    assert config.summary


def test_the_readable_names_of_the_builtin_configs_are_unique():
    """No 2 built-in configs share a readable name."""
    # --- act --------------------------
    readable_names = [config.readable_name for config in _BUILTIN_CONFIGS]

    # --- assert -----------------------
    assert len(set(readable_names)) == len(readable_names)
