"""`FeatureVectorDefinition` names its features, computes a candidate's raw features in natural units, fits 1 scale per
block on the log scale of the solvers block, and builds the matrix with each block divided by its scale."""

import numpy as np
import pytest
from snuffled import FunctionProperty, RootProperty

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, max_fevals_for
from sunnbear._core.benchmark.suites.pipeline.features import (
    SNUFFLED_PROPERTIES,
    SOLVERS_GPQ_LEVELS,
    FeatureBlock,
    FeatureBlockScales,
    FeatureMatrix,
    FeatureVectorDefinition,
    map_fevals_to_feature,
)
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.stats import gpq, mean_pairwise_l1

_DEFINITION = FeatureVectorDefinition(solver_ids=("regula_falsi", "bisection"))
_N_SOLVERS_FEATURES = 2 + len(SOLVERS_GPQ_LEVELS)
_MAX_FEVALS = max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)


def _raw_features(n_candidates: int) -> FeatureMatrix:
    """Return random raw features of `n_candidates` candidates, with evaluation counts in [2, max_fevals]."""
    rng = np.random.default_rng(seed=1)
    values = np.hstack(
        [
            rng.uniform(2, _MAX_FEVALS, size=(n_candidates, _N_SOLVERS_FEATURES)),
            rng.random((n_candidates, len(SNUFFLED_PROPERTIES))),
        ]
    )
    problem_ids = tuple(ProblemId.from_string(f"f99.{idx + 1}") for idx in range(n_candidates))
    return FeatureMatrix(problem_ids=problem_ids, values=values)


def test_the_names_hold_1_geomean_per_config_9_gpq_levels_and_10_properties():
    """For 2 configs, the names are the 2 geomeans in their order, the gpq levels 10 to 90, then snuffled's 10
    properties."""
    # --- act --------------------------
    feature_names = _DEFINITION.feature_names

    # --- assert -----------------------
    assert feature_names == (
        "solvers_geomean_regula_falsi",
        "solvers_geomean_bisection",
        *(f"solvers_gpq_{level}" for level in range(10, 100, 10)),
        *(f"snuffled_{prop.value}" for prop in SNUFFLED_PROPERTIES),
    )
    assert set(SNUFFLED_PROPERTIES) == {*RootProperty, *FunctionProperty}


def test_the_definition_takes_the_configs_in_their_order_and_needs_1():
    """`from_core_solver_configs` keeps the configs' order, and a definition without configs is refused."""
    # --- arrange ----------------------
    configs = [SolverConfigRegistry.config_from_id(solver_id) for solver_id in ["regula_falsi", "bisection"]]

    # --- act / assert -----------------
    assert FeatureVectorDefinition.from_core_solver_configs(configs) == _DEFINITION
    with pytest.raises(ValueError, match="at least 1 core solver config"):
        FeatureVectorDefinition.from_core_solver_configs([])


def test_the_raw_features_are_geomeans_pooled_gpqs_and_property_means():
    """Per config the geometric mean of its column, the gpq levels of all solves together, and the mean of each
    property, all in natural units."""
    # --- arrange ----------------------
    n_fevals_eff = np.array([[2.0, 8.0], [8.0, 32.0]])
    snuffled_property_values = np.vstack([np.zeros(len(SNUFFLED_PROPERTIES)), np.ones(len(SNUFFLED_PROPERTIES))])

    # --- act --------------------------
    raw_features = _DEFINITION.compute_raw_features(
        n_fevals_eff=n_fevals_eff, snuffled_property_values=snuffled_property_values
    )

    # --- assert -----------------------
    expected_gpqs = [gpq([2.0, 8.0, 8.0, 32.0], level) for level in SOLVERS_GPQ_LEVELS]
    np.testing.assert_allclose(raw_features, [4.0, 16.0, *expected_gpqs, *[0.5] * len(SNUFFLED_PROPERTIES)])
    assert raw_features[2 + SOLVERS_GPQ_LEVELS.index(0.5)] == pytest.approx(8.0)


@pytest.mark.parametrize(
    "n_configs, n_properties, message",
    [(3, len(SNUFFLED_PROPERTIES), "per config"), (2, len(SNUFFLED_PROPERTIES) - 1, "per property")],
)
def test_the_raw_features_refuse_arrays_with_the_wrong_columns(n_configs: int, n_properties: int, message: str):
    """An array with a column too many or too few is refused."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        _DEFINITION.compute_raw_features(
            n_fevals_eff=np.full((4, n_configs), 2.0), snuffled_property_values=np.zeros((2, n_properties))
        )


def test_each_blocks_scale_is_its_mean_pairwise_l1_distance_on_the_log_scale():
    """The solvers block's scale is computed after `map_fevals_to_feature`, the snuffled block's on its raw values."""
    # --- arrange ----------------------
    raw_features = _raw_features(5)

    # --- act --------------------------
    block_scales = _DEFINITION.fit_block_scales(raw_features)

    # --- assert -----------------------
    solvers_values = map_fevals_to_feature(raw_features.values[:, :_N_SOLVERS_FEATURES], max_fevals=_MAX_FEVALS)
    assert block_scales == FeatureBlockScales(
        scale_per_block={
            FeatureBlock.SOLVERS: mean_pairwise_l1(solvers_values),
            FeatureBlock.SNUFFLED: mean_pairwise_l1(raw_features.values[:, _N_SOLVERS_FEATURES:]),
        }
    )


def test_fewer_than_2_candidates_have_no_scales():
    """1 candidate has no pair, so no scale."""
    # --- act / assert -----------------
    assert _DEFINITION.fit_block_scales(_raw_features(1)) is None


def test_the_matrix_divides_each_block_on_the_log_scale_by_its_scale():
    """The matrix keeps the ids and the raw features, unchanged; each of its blocks has a mean pairwise L1 distance of 1
    over the candidates that the scales were fitted on."""
    # --- arrange ----------------------
    raw_features = _raw_features(5)
    raw_values = raw_features.values.copy()
    block_scales = _DEFINITION.fit_block_scales(raw_features)

    # --- act --------------------------
    matrix = _DEFINITION.build_scaled_matrix(raw_features, block_scales)

    # --- assert -----------------------
    assert matrix.problem_ids == raw_features.problem_ids
    np.testing.assert_array_equal(raw_features.values, raw_values)
    solvers_values = map_fevals_to_feature(raw_values[:, :_N_SOLVERS_FEATURES], max_fevals=_MAX_FEVALS)
    np.testing.assert_allclose(
        matrix.values[:, :_N_SOLVERS_FEATURES], solvers_values / block_scales.scale_per_block[FeatureBlock.SOLVERS]
    )
    np.testing.assert_allclose(
        matrix.values[:, _N_SOLVERS_FEATURES:],
        raw_values[:, _N_SOLVERS_FEATURES:] / block_scales.scale_per_block[FeatureBlock.SNUFFLED],
    )
    assert mean_pairwise_l1(matrix.values[:, :_N_SOLVERS_FEATURES]) == pytest.approx(1.0)
    assert mean_pairwise_l1(matrix.values[:, _N_SOLVERS_FEATURES:]) == pytest.approx(1.0)
