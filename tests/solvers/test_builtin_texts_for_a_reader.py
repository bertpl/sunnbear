"""These tests assert that every built-in solver and solver config states what a reader sees of it: a readable name,
whether the solver brackets, and a summary of each config."""

import pytest

from sunnbear._core.utils.class_origin import is_sunnbear_module
from sunnbear.solvers import SolverConfigRegistry

_BUILTIN_CONFIGS = [config for config in SolverConfigRegistry.configs() if config.role.is_builtin_only]
_BUILTIN_SOLVER_CLASSES = sorted(
    {
        config.solver_cls
        for config in SolverConfigRegistry.configs()
        if is_sunnbear_module(config.solver_cls.__module__)
    },
    key=lambda solver_cls: solver_cls.__name__,
)


@pytest.mark.parametrize("solver_cls", _BUILTIN_SOLVER_CLASSES, ids=lambda solver_cls: solver_cls.__name__)
def test_a_builtin_solver_states_its_readable_name_and_whether_it_brackets_as_its_package_says(solver_cls):
    """A built-in solver has a readable name, and it is bracketing exactly when its class lives in the package of the
    bracketing solvers."""
    assert solver_cls.readable_name
    assert solver_cls.is_bracketing is solver_cls.__module__.startswith("sunnbear._core.solvers.bracketing.")


@pytest.mark.parametrize("config", _BUILTIN_CONFIGS, ids=lambda config: config.solver_id)
def test_a_builtin_config_has_a_readable_name_and_a_summary(config):
    """A built-in config has a readable name and a summary that is not empty."""
    assert config.readable_name
    assert config.summary


def test_the_readable_names_of_the_builtin_configs_are_unique():
    """No 2 built-in configs share a readable name."""
    readable_names = [config.readable_name for config in _BUILTIN_CONFIGS]
    assert len(set(readable_names)) == len(readable_names)
