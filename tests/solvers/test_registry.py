"""`SolverConfigRegistry` holds the built-in configs on import and rejects a config that conflicts with another."""

import pytest

from sunnbear._core.solvers.bracketing.bisection.configs import BisectionConfig
from sunnbear._core.solvers.bracketing.illinois.configs import IllinoisConfig
from sunnbear._core.solvers.bracketing.regula_falsi.configs import RegulaFalsiConfig
from sunnbear._core.solvers.bracketing.ridders.configs import (
    RiddersCorrectedCriterionConfig,
    RiddersOriginalCriterionConfig,
)
from sunnbear.exceptions import UnknownSolverConfigError
from sunnbear.solvers import Bisection, Illinois, RegulaFalsi, Ridders, SolverConfigRegistry, SolverRole

from .example_solvers import WeightedSplitSolver, define_config


# ==================================================================================================
#  Built-in configs
# ==================================================================================================
@pytest.mark.parametrize(
    "config_cls, solver_id, solver_cls, role",
    [
        (BisectionConfig, "bisection", Bisection, SolverRole.BUILTIN_BASELINE),
        (IllinoisConfig, "illinois", Illinois, SolverRole.BUILTIN_CORE),
        (RegulaFalsiConfig, "regula_falsi", RegulaFalsi, SolverRole.BUILTIN_SECONDARY),
        (
            RiddersCorrectedCriterionConfig,
            "ridders[stopping_criterion='corrected']",
            Ridders,
            SolverRole.BUILTIN_SECONDARY,
        ),
        (RiddersOriginalCriterionConfig, "ridders[stopping_criterion='original']", Ridders, SolverRole.BUILTIN_CORE),
    ],
)
def test_built_in_config_is_registered_on_import(config_cls, solver_id, solver_cls, role):
    # --- act --------------------------
    config = SolverConfigRegistry.config_from_id(solver_id)

    # --- assert -----------------------
    assert type(config) is config_cls
    assert type(config.instantiate()) is solver_cls
    assert config.role is role


# ==================================================================================================
#  Enumeration and lookup
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_configs_are_sorted_by_solver_id_and_solver_classes_are_unique():
    # --- arrange ----------------------
    for weight in (0.75, 0.25):
        define_config(
            {"solver_cls": WeightedSplitSolver, "solver_kwargs": {"weight": weight}, "role": SolverRole.USER_ACTIVE}
        )

    # --- act --------------------------
    solver_ids = [config.solver_id for config in SolverConfigRegistry.configs()]
    solver_classes = SolverConfigRegistry.solver_classes()

    # --- assert -----------------------
    assert solver_ids == [
        "bisection",
        "illinois",
        "regula_falsi",
        "ridders[stopping_criterion='corrected']",
        "ridders[stopping_criterion='original']",
        "weighted_split[weight=0.25]",
        "weighted_split[weight=0.75]",
    ]
    assert solver_classes == (Bisection, Illinois, RegulaFalsi, Ridders, WeightedSplitSolver)


def test_config_from_id_rejects_an_unknown_id():
    with pytest.raises(UnknownSolverConfigError, match="'secant'"):
        SolverConfigRegistry.config_from_id("secant")


# ==================================================================================================
#  Checks across configs
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_duplicate_solver_id_is_rejected():
    # --- arrange ----------------------
    namespace = {"solver_cls": Bisection, "role": SolverRole.USER_ACTIVE}

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="Duplicate solver_id 'bisection'"):
        define_config(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_second_baseline_is_rejected():
    # --- arrange ----------------------
    namespace = {
        "__module__": "sunnbear.hypothetical_solvers",
        "solver_cls": WeightedSplitSolver,
        "solver_kwargs": {"weight": 0.5},
        "role": SolverRole.BUILTIN_BASELINE,
    }

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="Only one config may have role BUILTIN_BASELINE"):
        define_config(namespace)
