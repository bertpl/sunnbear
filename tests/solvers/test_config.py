"""A `SolverConfig` builds its identity and its solver from its declaration, and a malformed one fails at definition."""

import pytest

from sunnbear.solvers import BracketingSolver, SolverConfigRegistry, SolverRole
from tests.solvers.example_solvers import WeightedSplitSolver, define_config


# ==================================================================================================
#  Test-local solver
# ==================================================================================================
class _AbstractSolver(BracketingSolver):
    """`_AbstractSolver` leaves `_next_x` unimplemented."""

    name = "abstract"
    version = 1


# ==================================================================================================
#  Identity and construction
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize(
    "kwargs, solver_id_expected",
    [
        ({"weight": 0.25}, "weighted_split[weight=0.25]"),
        ({"weight": 0.25, "n_warmup": 3}, "weighted_split[n_warmup=3,weight=0.25]"),
        ({"n_warmup": 3, "weight": 0.25}, "weighted_split[n_warmup=3,weight=0.25]"),
    ],
)
def test_solver_id_lists_init_arguments_sorted_by_name(kwargs, solver_id_expected):
    # --- arrange ----------------------
    config_cls = define_config({"solver_cls": WeightedSplitSolver, "kwargs": kwargs, "role": SolverRole.USER_ACTIVE})

    # --- act / assert -----------------
    assert config_cls().solver_id == solver_id_expected


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_instantiate_passes_the_init_arguments():
    # --- arrange ----------------------
    config_cls = define_config(
        {"solver_cls": WeightedSplitSolver, "kwargs": {"weight": 0.25, "n_warmup": 3}, "role": SolverRole.USER_ACTIVE}
    )

    # --- act --------------------------
    solver = config_cls().instantiate()

    # --- assert -----------------------
    assert isinstance(solver, WeightedSplitSolver)
    assert (solver.weight, solver.n_warmup) == (0.25, 3)


# ==================================================================================================
#  Validation at class definition
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize(
    "namespace, message",
    [
        ({"role": SolverRole.USER_ACTIVE}, "must define solver_cls"),
        ({"solver_cls": WeightedSplitSolver, "kwargs": {"weight": 0.5}}, "must define role"),
        ({"solver_cls": int, "role": SolverRole.USER_ACTIVE}, "must be a Solver subclass"),
        ({"solver_cls": _AbstractSolver, "role": SolverRole.USER_ACTIVE}, "_AbstractSolver is abstract"),
        ({"solver_cls": WeightedSplitSolver, "role": SolverRole.USER_ACTIVE}, "missing a required argument"),
        (
            {"solver_cls": WeightedSplitSolver, "kwargs": {"weight": 0.5, "slack": 1}, "role": SolverRole.USER_ACTIVE},
            "unexpected keyword argument 'slack'",
        ),
        (
            {"solver_cls": WeightedSplitSolver, "kwargs": {"weight": [0.5]}, "role": SolverRole.USER_ACTIVE},
            r"kwargs\['weight'\] must be a bool, int, float, or str",
        ),
    ],
)
def test_malformed_config_is_rejected_at_class_definition(namespace, message):
    with pytest.raises(TypeError, match=message):
        define_config(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize("role", [role for role in SolverRole if role.is_sealed])
def test_sealed_role_outside_sunnbear_is_rejected(role):
    # --- arrange ----------------------
    namespace = {"solver_cls": WeightedSplitSolver, "kwargs": {"weight": 0.5}, "role": role}

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="reserved for configs inside the sunnbear package"):
        define_config(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_sealed_role_inside_sunnbear_is_accepted():
    # --- arrange ----------------------
    namespace = {
        "__module__": "sunnbear.hypothetical_solvers",
        "solver_cls": WeightedSplitSolver,
        "kwargs": {"weight": 0.5},
        "role": SolverRole.BUILTIN_CORE,
    }

    # --- act --------------------------
    define_config(namespace)

    # --- assert -----------------------
    assert SolverConfigRegistry.config_from_id("weighted_split[weight=0.5]").role is SolverRole.BUILTIN_CORE
