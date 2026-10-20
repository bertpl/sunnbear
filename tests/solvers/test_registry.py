"""`SolverConfigRegistry` holds the built-in configs on import and rejects a config that conflicts with another."""

import pytest

from sunnbear._core.utils.class_origin import is_sunnbear_module
from sunnbear.exceptions import UnknownSolverConfigError
from sunnbear.solvers import (
    CARF,
    ITP,
    TOMS748,
    AndersonBjorck,
    Bisection,
    Brent,
    Chandrupatla,
    Ellithy,
    Ford,
    Illinois,
    ModAB,
    ModABSafeguarded,
    Pegasus,
    RegulaFalsi,
    Ridders,
    Secant,
    SolverConfig,
    SolverConfigRegistry,
    SolverRole,
    SteffenBrent,
)

from .example_solvers import WeightedSplitSolver, define_configs_declaration

# ==================================================================================================
#  Built-in configs
# ==================================================================================================
# Each row holds a built-in config: its solver_id, its solver class and its role.
_BUILT_IN_CONFIG_ROWS = [
    ("anderson_bjorck", AndersonBjorck, SolverRole.BUILTIN_SECONDARY),
    ("bisection", Bisection, SolverRole.BUILTIN_BASELINE),
    ("brent[variant='hyperbolic']", Brent, SolverRole.BUILTIN_SECONDARY),
    ("brent[variant='inverse_quadratic']", Brent, SolverRole.BUILTIN_CORE),
    ("carf", CARF, SolverRole.BUILTIN_SECONDARY),
    ("chandrupatla", Chandrupatla, SolverRole.BUILTIN_CORE),
    ("ellithy[variant='bf']", Ellithy, SolverRole.BUILTIN_SECONDARY),
    ("ellithy[variant='bfms']", Ellithy, SolverRole.BUILTIN_SECONDARY),
    ("ellithy[variant='tf']", Ellithy, SolverRole.BUILTIN_SECONDARY),
    ("ellithy[variant='tfms']", Ellithy, SolverRole.BUILTIN_SECONDARY),
    ("ford[variant='method_1']", Ford, SolverRole.BUILTIN_SECONDARY),
    ("ford[variant='method_3']", Ford, SolverRole.BUILTIN_SECONDARY),
    ("ford[variant='method_4']", Ford, SolverRole.BUILTIN_SECONDARY),
    ("illinois", Illinois, SolverRole.BUILTIN_CORE),
    ("itp[n_slack=0,variant='paper_experiments']", ITP, SolverRole.BUILTIN_CORE),
    ("itp[n_slack=0,variant='paper_pseudocode']", ITP, SolverRole.BUILTIN_SECONDARY),
    ("itp[n_slack=4,variant='paper_experiments']", ITP, SolverRole.BUILTIN_SECONDARY),
    ("modab", ModAB, SolverRole.BUILTIN_SECONDARY),
    ("modab_safeguarded", ModABSafeguarded, SolverRole.BUILTIN_SECONDARY),
    ("pegasus", Pegasus, SolverRole.BUILTIN_SECONDARY),
    ("regula_falsi", RegulaFalsi, SolverRole.BUILTIN_SECONDARY),
    ("ridders[variant='commons_math']", Ridders, SolverRole.BUILTIN_SECONDARY),
    ("ridders[variant='scipy']", Ridders, SolverRole.BUILTIN_SECONDARY),
    ("ridders[variant='standard_stopping_criterion']", Ridders, SolverRole.BUILTIN_CORE),
    ("secant", Secant, SolverRole.BUILTIN_SECONDARY),
    ("steffen_brent", SteffenBrent, SolverRole.BUILTIN_SECONDARY),
    ("toms748[k=1]", TOMS748, SolverRole.BUILTIN_SECONDARY),
    ("toms748[k=2]", TOMS748, SolverRole.BUILTIN_CORE),
]


@pytest.mark.parametrize("solver_id, solver_cls, role", _BUILT_IN_CONFIG_ROWS)
def test_built_in_config_is_registered_on_import(solver_id, solver_cls, role):
    """On import, each built-in config is registered under its ``solver_id``, with its solver class and its role, as
    declared inside the sunnbear package."""
    # --- act --------------------------
    config = SolverConfigRegistry.config_from_id(solver_id)

    # --- assert -----------------------
    assert config.solver_cls is solver_cls
    assert type(config.instantiate()) is solver_cls
    assert config.role is role
    assert is_sunnbear_module(config.declaring_module_name)


def test_the_built_in_config_rows_name_every_built_in_config():
    """`_BUILT_IN_CONFIG_ROWS` names every config that importing sunnbear registers, and no other."""
    # --- act / assert -----------------
    assert {row[0] for row in _BUILT_IN_CONFIG_ROWS} == {
        config.solver_id
        for config in SolverConfigRegistry.configs()
        if is_sunnbear_module(config.declaring_module_name)
    }


# ==================================================================================================
#  Enumeration and lookup
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_configs_are_sorted_by_solver_id_and_solver_classes_are_unique():
    """`SolverConfigRegistry.configs` lists every config sorted by ``solver_id``, and
    `SolverConfigRegistry.solver_classes` lists each solver class once, in that order."""
    # --- arrange ----------------------
    configs = tuple(
        SolverConfig(solver_cls=WeightedSplitSolver, role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": weight})
        for weight in (0.75, 0.25)
    )
    define_configs_declaration({"configs": configs})

    # --- act --------------------------
    solver_ids = [config.solver_id for config in SolverConfigRegistry.configs()]
    solver_classes = SolverConfigRegistry.solver_classes()

    # --- assert -----------------------
    assert solver_ids == [
        "anderson_bjorck",
        "bisection",
        "brent[variant='hyperbolic']",
        "brent[variant='inverse_quadratic']",
        "carf",
        "chandrupatla",
        "ellithy[variant='bf']",
        "ellithy[variant='bfms']",
        "ellithy[variant='tf']",
        "ellithy[variant='tfms']",
        "ford[variant='method_1']",
        "ford[variant='method_3']",
        "ford[variant='method_4']",
        "illinois",
        "itp[n_slack=0,variant='paper_experiments']",
        "itp[n_slack=0,variant='paper_pseudocode']",
        "itp[n_slack=4,variant='paper_experiments']",
        "modab",
        "modab_safeguarded",
        "pegasus",
        "regula_falsi",
        "ridders[variant='commons_math']",
        "ridders[variant='scipy']",
        "ridders[variant='standard_stopping_criterion']",
        "secant",
        "steffen_brent",
        "toms748[k=1]",
        "toms748[k=2]",
        "weighted_split[weight=0.25]",
        "weighted_split[weight=0.75]",
    ]
    assert solver_classes == (
        AndersonBjorck,
        Bisection,
        Brent,
        CARF,
        Chandrupatla,
        Ellithy,
        Ford,
        Illinois,
        ITP,
        ModAB,
        ModABSafeguarded,
        Pegasus,
        RegulaFalsi,
        Ridders,
        Secant,
        SteffenBrent,
        TOMS748,
        WeightedSplitSolver,
    )


def test_config_from_id_rejects_an_unknown_id():
    """For an unregistered id, `SolverConfigRegistry.config_from_id` raises `UnknownSolverConfigError` naming that
    id."""
    # --- act / assert -----------------
    with pytest.raises(UnknownSolverConfigError, match="'newton'"):
        SolverConfigRegistry.config_from_id("newton")


# ==================================================================================================
#  Checks across configs
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_duplicate_solver_id_is_rejected():
    """Declaring a config with the ``solver_id`` of a registered config raises ``ValueError``."""
    # --- arrange ----------------------
    namespace = {"configs": (SolverConfig(solver_cls=Bisection, role=SolverRole.USER_ACTIVE),)}

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="Duplicate solver_id 'bisection'"):
        define_configs_declaration(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_second_baseline_is_rejected():
    """Declaring a second config with role ``BUILTIN_BASELINE`` raises ``ValueError``."""
    # --- arrange ----------------------
    namespace = {
        "__module__": "sunnbear.hypothetical_solvers",
        "configs": (
            SolverConfig(
                solver_cls=WeightedSplitSolver, role=SolverRole.BUILTIN_BASELINE, solver_kwargs={"weight": 0.5}
            ),
        ),
    }

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="Only one config may have role BUILTIN_BASELINE"):
        define_configs_declaration(namespace)
