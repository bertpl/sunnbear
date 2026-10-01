"""`generate_mc_tuples` builds a nested set that is a Latin hypercube at every size it builds."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import generate_mc_tuples
from sunnbear._core.benchmark.mc_tuples.construction_steps import CANDIDATES_PER_CELL, MCTuplesConstructionStep
from sunnbear._core.benchmark.mc_tuples.latin_hypercube_grid import LatinHypercubeGrid


@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_latin_hypercubes():
    """A 1 s construction builds sizes 32 and 64; each is a Latin hypercube, and size 32 is the start of size 64.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0)

    # --- assert -----------------------
    assert tuples.size == 64
    assert LatinHypercubeGrid.is_latin_hypercube(tuples.first(32))
    assert LatinHypercubeGrid.is_latin_hypercube(tuples)
    assert np.unique(tuples.u).size == np.unique(tuples.v).size == 64


@pytest.mark.parametrize(
    "size, step, pool_size",
    [
        (32, MCTuplesConstructionStep.CELL_SELECTION, 32 * 32),  # all cells, no size below
        (32, MCTuplesConstructionStep.REFINEMENT, CANDIDATES_PER_CELL * 32),
        (1024, MCTuplesConstructionStep.CELL_SELECTION, 512 * 512 + 512),  # the free cells and the size below
        (1024, MCTuplesConstructionStep.REFINEMENT, CANDIDATES_PER_CELL * 512 + 512),
    ],
)
def test_pool_size_counts_the_new_candidates_and_the_size_below(size, step, pool_size):
    """A step's pool holds its new candidates and, above the smallest size, the tuples of the size below."""
    # --- act / assert -----------------
    assert step.pool_size(size) == pool_size
