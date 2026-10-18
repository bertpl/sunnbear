"""A `SolverConfig` builds its identity and its solver from its declaration in a `SolverConfigs` subclass, and a
malformed declaration fails at definition."""

import pytest

from sunnbear.solvers import BracketingSolver, SolverConfig, SolverConfigRegistry, SolverRole

from .example_solvers import WeightedSplitSolver, define_configs


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
    "solver_kwargs, solver_id_expected",
    [
        ({"weight": 0.25}, "weighted_split[weight=0.25]"),
        ({"weight": 0.25, "n_warmup": 3}, "weighted_split[n_warmup=3,weight=0.25]"),
        ({"n_warmup": 3, "weight": 0.25}, "weighted_split[n_warmup=3,weight=0.25]"),
    ],
)
def test_solver_id_lists_init_arguments_sorted_by_name(solver_kwargs, solver_id_expected):
    """A config's ``solver_id`` is the solver name followed by its init arguments, sorted by name whatever their order
    in ``solver_kwargs``."""
    # --- arrange ----------------------
    configs = (SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs=solver_kwargs),)

    # --- act --------------------------
    define_configs({"solver_cls": WeightedSplitSolver, "configs": configs})

    # --- assert -----------------------
    assert SolverConfigRegistry.config_from_id(solver_id_expected).solver_id == solver_id_expected


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_instantiate_passes_the_init_arguments():
    """`SolverConfig.instantiate` builds an instance of the config's solver class from its ``solver_kwargs``."""
    # --- arrange ----------------------
    configs = (SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.25, "n_warmup": 3}),)
    define_configs({"solver_cls": WeightedSplitSolver, "configs": configs})

    # --- act --------------------------
    solver = SolverConfigRegistry.config_from_id("weighted_split[n_warmup=3,weight=0.25]").instantiate()

    # --- assert -----------------------
    assert isinstance(solver, WeightedSplitSolver)
    assert (solver.weight, solver.n_warmup) == (0.25, 3)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_every_config_of_a_declaration_is_registered_with_its_solver_class_and_module():
    """Each config of a `SolverConfigs` subclass is registered with the subclass's ``solver_cls``, and with the
    subclass's module, which a benchmark worker imports."""
    # --- arrange ----------------------
    configs = (
        SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.25}),
        SolverConfig(role=SolverRole.USER_OTHER, solver_kwargs={"weight": 0.75}),
    )

    # --- act --------------------------
    define_configs({"solver_cls": WeightedSplitSolver, "configs": configs})

    # --- assert -----------------------
    registered = [SolverConfigRegistry.config_from_id(f"weighted_split[weight={w}]") for w in (0.25, 0.75)]
    assert [(c.solver_cls, c.module_name, c.role) for c in registered] == [
        (WeightedSplitSolver, "tests.solvers", SolverRole.USER_ACTIVE),
        (WeightedSplitSolver, "tests.solvers", SolverRole.USER_OTHER),
    ]


# ==================================================================================================
#  Validation at class definition
# ==================================================================================================
@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize(
    "namespace, message",
    [
        ({"configs": (SolverConfig(role=SolverRole.USER_ACTIVE),)}, "must define solver_cls"),
        ({"solver_cls": WeightedSplitSolver}, "must define configs"),
        ({"solver_cls": int, "configs": (SolverConfig(role=SolverRole.USER_ACTIVE),)}, "must be a Solver subclass"),
        (
            {"solver_cls": _AbstractSolver, "configs": (SolverConfig(role=SolverRole.USER_ACTIVE),)},
            "_AbstractSolver is abstract",
        ),
        ({"solver_cls": WeightedSplitSolver, "configs": ()}, "must be a non-empty tuple"),
        (
            {"solver_cls": WeightedSplitSolver, "configs": [SolverConfig(role=SolverRole.USER_ACTIVE)]},
            "must be a non-empty tuple",
        ),
        ({"solver_cls": WeightedSplitSolver, "configs": ({"weight": 0.5},)}, "must hold only SolverConfig values"),
        (
            {"solver_cls": WeightedSplitSolver, "configs": (SolverConfig(role=SolverRole.USER_ACTIVE),)},
            "missing a required argument",
        ),
        (
            {
                "solver_cls": WeightedSplitSolver,
                "configs": (SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.5, "slack": 1}),),
            },
            "unexpected keyword argument 'slack'",
        ),
        (
            {
                "solver_cls": WeightedSplitSolver,
                "configs": (SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": [0.5]}),),
            },
            r"solver_kwargs\['weight'\] must be a bool, int, float, or str",
        ),
    ],
)
def test_malformed_declaration_is_rejected_at_class_definition(namespace, message):
    """Defining a `SolverConfigs` subclass raises ``TypeError`` when it lacks ``solver_cls`` or ``configs``, when
    ``solver_cls`` is not a concrete `Solver` subclass, when ``configs`` is not a non-empty tuple of `SolverConfig`
    values, or when a config's ``solver_kwargs`` does not match ``__init__`` or holds an unsupported type."""
    # --- act / assert -----------------
    with pytest.raises(TypeError, match=message):
        define_configs(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_a_malformed_declaration_registers_none_of_its_configs():
    """When 1 config of a declaration is malformed, the configs before it are not registered either."""
    # --- arrange ----------------------
    configs = (
        SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.5}),
        SolverConfig(role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.5, "slack": 1}),
    )

    # --- act --------------------------
    with pytest.raises(TypeError):
        define_configs({"solver_cls": WeightedSplitSolver, "configs": configs})

    # --- assert -----------------------
    assert "weighted_split[weight=0.5]" not in {config.solver_id for config in SolverConfigRegistry.configs()}


@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize("role", [role for role in SolverRole if role.is_builtin_only])
def test_builtin_only_role_outside_sunnbear_is_rejected(role):
    """Declaring a config outside the sunnbear package with a built-in-only role raises ``ValueError``."""
    # --- arrange ----------------------
    namespace = {
        "solver_cls": WeightedSplitSolver,
        "configs": (SolverConfig(role=role, solver_kwargs={"weight": 0.5}),),
    }

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="reserved for configs inside the sunnbear package"):
        define_configs(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_builtin_only_role_inside_sunnbear_is_accepted():
    """A config declared inside the sunnbear package can take a built-in-only role, and is registered with it."""
    # --- arrange ----------------------
    namespace = {
        "__module__": "sunnbear.hypothetical_solvers",
        "solver_cls": WeightedSplitSolver,
        "configs": (SolverConfig(role=SolverRole.BUILTIN_CORE, solver_kwargs={"weight": 0.5}),),
    }

    # --- act --------------------------
    define_configs(namespace)

    # --- assert -----------------------
    assert SolverConfigRegistry.config_from_id("weighted_split[weight=0.5]").role is SolverRole.BUILTIN_CORE
