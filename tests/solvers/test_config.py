"""A `SolverConfig` gets its `solver_id` from its solver class and init arguments, and is registered by its declaration
in a `SolverConfigsDeclaration` subclass; a malformed config or declaration fails when it is defined."""

import pytest

from sunnbear.solvers import BracketingSolver, SolverConfig, SolverConfigRegistry, SolverRole

from .example_solvers import WeightedSplitSolver, define_configs_declaration


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _AbstractSolver(BracketingSolver):
    """`_AbstractSolver` leaves `_next_x` unimplemented."""

    name = "abstract"
    version = 1


class _RenamedWeightedSplitSolver(WeightedSplitSolver):
    """`_RenamedWeightedSplitSolver` is `WeightedSplitSolver` under another name, a second solver class to declare."""

    name = "renamed_weighted_split"


# ==================================================================================================
#  Identity and construction
# ==================================================================================================
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
    # --- act --------------------------
    config = SolverConfig(solver_cls=WeightedSplitSolver, role=SolverRole.USER_ACTIVE, solver_kwargs=solver_kwargs)

    # --- assert -----------------------
    assert config.solver_id == solver_id_expected


def test_instantiate_passes_the_init_arguments():
    """`SolverConfig.instantiate` builds an instance of the config's solver class from its ``solver_kwargs``."""
    # --- arrange ----------------------
    config = SolverConfig(
        solver_cls=WeightedSplitSolver, role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.25, "n_warmup": 3}
    )

    # --- act --------------------------
    solver = config.instantiate()

    # --- assert -----------------------
    assert isinstance(solver, WeightedSplitSolver)
    assert (solver.weight, solver.n_warmup) == (0.25, 3)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_every_config_of_a_declaration_is_registered_with_its_own_solver_class_and_the_module():
    """Each config of a `SolverConfigsDeclaration` subclass is registered with its own ``solver_cls``, so 1 subclass can
    declare configs of 2 solver classes, and with the subclass's module, which a benchmark worker imports."""
    # --- arrange ----------------------
    configs = (
        SolverConfig(solver_cls=WeightedSplitSolver, role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.25}),
        SolverConfig(
            solver_cls=_RenamedWeightedSplitSolver, role=SolverRole.USER_OTHER, solver_kwargs={"weight": 0.75}
        ),
    )

    # --- act --------------------------
    define_configs_declaration({"configs": configs})

    # --- assert -----------------------
    registered_configs = [
        SolverConfigRegistry.config_from_id(solver_id)
        for solver_id in ("weighted_split[weight=0.25]", "renamed_weighted_split[weight=0.75]")
    ]
    assert [(c.solver_cls, c.declaring_module_name, c.role) for c in registered_configs] == [
        (WeightedSplitSolver, "tests.solvers", SolverRole.USER_ACTIVE),
        (_RenamedWeightedSplitSolver, "tests.solvers", SolverRole.USER_OTHER),
    ]


# ==================================================================================================
#  Validation at definition
# ==================================================================================================
@pytest.mark.parametrize(
    "solver_cls, solver_kwargs, message",
    [
        (int, {}, "must be a Solver subclass"),
        (_AbstractSolver, {}, "_AbstractSolver is abstract"),
        (WeightedSplitSolver, {"weight": [0.5]}, r"solver_kwargs\['weight'\] must be a bool, int, float, or str"),
        (WeightedSplitSolver, {}, "missing a required argument"),
        (WeightedSplitSolver, {"weight": 0.5, "slack": 1}, "unexpected keyword argument 'slack'"),
    ],
)
def test_malformed_config_is_rejected_when_built(solver_cls, solver_kwargs, message):
    """Building a `SolverConfig` whose solver class is not a concrete `Solver` subclass, or whose ``solver_kwargs`` do
    not fit that class or cannot be written as text by `solver_id`, raises ``TypeError`` that names the defect."""
    # --- act / assert -----------------
    with pytest.raises(TypeError, match=message):
        SolverConfig(solver_cls=solver_cls, role=SolverRole.USER_ACTIVE, solver_kwargs=solver_kwargs)


@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize(
    "namespace, message",
    [
        ({}, "must define configs"),
        ({"configs": ()}, "must be a non-empty tuple"),
        (
            {
                "configs": [
                    SolverConfig(
                        solver_cls=WeightedSplitSolver, role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.5}
                    )
                ]
            },
            "must be a non-empty tuple",
        ),
        ({"configs": ({"weight": 0.5},)}, "must hold only SolverConfig values"),
    ],
)
def test_malformed_declaration_is_rejected_at_class_definition(namespace, message):
    """Defining a `SolverConfigsDeclaration` subclass with malformed ``configs`` raises ``TypeError`` that names the
    defect."""
    # --- act / assert -----------------
    with pytest.raises(TypeError, match=message):
        define_configs_declaration(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_a_malformed_declaration_registers_none_of_its_configs():
    """When 1 entry of a `SolverConfigsDeclaration` subclass's ``configs`` is malformed, no config of that subclass is
    registered."""
    # --- arrange ----------------------
    configs = (
        SolverConfig(solver_cls=WeightedSplitSolver, role=SolverRole.USER_ACTIVE, solver_kwargs={"weight": 0.5}),
        {"weight": 0.75},
    )

    # --- act --------------------------
    with pytest.raises(TypeError):
        define_configs_declaration({"configs": configs})

    # --- assert -----------------------
    assert "weighted_split[weight=0.5]" not in {config.solver_id for config in SolverConfigRegistry.configs()}


@pytest.mark.usefixtures("isolated_solver_config_registry")
@pytest.mark.parametrize("role", [role for role in SolverRole if role.is_builtin_only])
def test_builtin_only_role_outside_sunnbear_is_rejected(role):
    """Declaring a config outside the sunnbear package with a built-in-only role raises ``ValueError``."""
    # --- arrange ----------------------
    namespace = {"configs": (SolverConfig(solver_cls=WeightedSplitSolver, role=role, solver_kwargs={"weight": 0.5}),)}

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="reserved for configs inside the sunnbear package"):
        define_configs_declaration(namespace)


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_builtin_only_role_inside_sunnbear_is_accepted():
    """A config declared inside the sunnbear package can take a built-in-only role, and is registered with it."""
    # --- arrange ----------------------
    namespace = {
        "__module__": "sunnbear.hypothetical_solvers",
        "configs": (
            SolverConfig(solver_cls=WeightedSplitSolver, role=SolverRole.BUILTIN_CORE, solver_kwargs={"weight": 0.5}),
        ),
    }

    # --- act --------------------------
    define_configs_declaration(namespace)

    # --- assert -----------------------
    assert SolverConfigRegistry.config_from_id("weighted_split[weight=0.5]").role is SolverRole.BUILTIN_CORE
