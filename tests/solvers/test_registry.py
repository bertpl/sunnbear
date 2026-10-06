"""`SolverConfigRegistry` holds the built-in configs on import and rejects a config that conflicts with another."""

import pytest

from sunnbear._core.solvers.bracketing.bisection.configs import BisectionConfig
from sunnbear._core.solvers.bracketing.brent.configs import BrentConfig
from sunnbear._core.solvers.bracketing.chandrupatla.configs import ChandrupatlaConfig
from sunnbear._core.solvers.bracketing.illinois.configs import IllinoisConfig
from sunnbear._core.solvers.bracketing.itp.configs import (
    ITPPaperExperimentsSlack0Config,
    ITPPaperExperimentsSlack4Config,
    ITPPaperPseudocodeSlack0Config,
)
from sunnbear._core.solvers.bracketing.pegasus.configs import PegasusConfig
from sunnbear._core.solvers.bracketing.regula_falsi.configs import RegulaFalsiConfig
from sunnbear._core.solvers.bracketing.ridders.configs import (
    RiddersBracketingSolverConfig,
    RiddersCommonsMathConfig,
    RiddersScipyConfig,
)
from sunnbear._core.solvers.bracketing.toms748.configs import TOMS748K1Config, TOMS748K2Config
from sunnbear.exceptions import UnknownSolverConfigError
from sunnbear.solvers import (
    ITP,
    TOMS748,
    Bisection,
    Brent,
    Chandrupatla,
    Illinois,
    Pegasus,
    RegulaFalsi,
    Ridders,
    SolverConfigRegistry,
    SolverRole,
)

from .example_solvers import WeightedSplitSolver, define_config


# ==================================================================================================
#  Built-in configs
# ==================================================================================================
@pytest.mark.parametrize(
    "config_cls, solver_id, solver_cls, role",
    [
        (BisectionConfig, "bisection", Bisection, SolverRole.BUILTIN_BASELINE),
        (BrentConfig, "brent", Brent, SolverRole.BUILTIN_CORE),
        (IllinoisConfig, "illinois", Illinois, SolverRole.BUILTIN_CORE),
        (
            ITPPaperExperimentsSlack0Config,
            "itp[n_slack=0,variant='paper_experiments']",
            ITP,
            SolverRole.BUILTIN_SECONDARY,
        ),
        (
            ITPPaperPseudocodeSlack0Config,
            "itp[n_slack=0,variant='paper_pseudocode']",
            ITP,
            SolverRole.BUILTIN_SECONDARY,
        ),
        (ITPPaperExperimentsSlack4Config, "itp[n_slack=4,variant='paper_experiments']", ITP, SolverRole.BUILTIN_CORE),
        (PegasusConfig, "pegasus", Pegasus, SolverRole.BUILTIN_SECONDARY),
        (RegulaFalsiConfig, "regula_falsi", RegulaFalsi, SolverRole.BUILTIN_SECONDARY),
        (
            RiddersBracketingSolverConfig,
            "ridders[variant='bracketing_solver']",
            Ridders,
            SolverRole.BUILTIN_SECONDARY,
        ),
        (RiddersCommonsMathConfig, "ridders[variant='commons_math']", Ridders, SolverRole.BUILTIN_SECONDARY),
        (RiddersScipyConfig, "ridders[variant='scipy']", Ridders, SolverRole.BUILTIN_CORE),
        (ChandrupatlaConfig, "chandrupatla", Chandrupatla, SolverRole.BUILTIN_CORE),
        (TOMS748K1Config, "toms748[k=1]", TOMS748, SolverRole.BUILTIN_CORE),
        (TOMS748K2Config, "toms748[k=2]", TOMS748, SolverRole.BUILTIN_SECONDARY),
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
        "brent",
        "chandrupatla",
        "illinois",
        "itp[n_slack=0,variant='paper_experiments']",
        "itp[n_slack=0,variant='paper_pseudocode']",
        "itp[n_slack=4,variant='paper_experiments']",
        "pegasus",
        "regula_falsi",
        "ridders[variant='bracketing_solver']",
        "ridders[variant='commons_math']",
        "ridders[variant='scipy']",
        "toms748[k=1]",
        "toms748[k=2]",
        "weighted_split[weight=0.25]",
        "weighted_split[weight=0.75]",
    ]
    assert solver_classes == (
        Bisection,
        Brent,
        Chandrupatla,
        Illinois,
        ITP,
        Pegasus,
        RegulaFalsi,
        Ridders,
        TOMS748,
        WeightedSplitSolver,
    )


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
