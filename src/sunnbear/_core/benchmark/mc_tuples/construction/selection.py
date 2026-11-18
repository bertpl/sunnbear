"""`MCTuplesSelectionSolve` picks a size's new base tuples from its population in the size's first max-div solve.

A size holds exactly 1 tuple in each of its LHS lanes and tiles when its base tuples' values fill its lower-half LHS
lanes, 1 value per lane, and its base tuples fill its tiles in [0, 0.5]^2, the lower-half tiles, 1 per tile
(`rotations`).

Each LHS lane of the size below spans 4 LHS lanes of the size, and each of its tiles spans 2 by 2 tiles of the size;
the size below's base tuples fill exactly 1 of these lanes and 1 of these tiles. The lanes and tiles that they leave are
the free lanes and the free tiles.

The size's new base tuples fill them exactly: their u and v values are as many as the free lanes, and the new base
tuples are as many as the free tiles.

The population lies in the free tiles, in the LHS cells of the free lanes, except the diagonal cells, whose u and v
share an LHS lane (`MCTuplesPopulation.draw_in_off_diagonal_cells`). A candidate anywhere else could never be picked:

- a lane that the size below uses would hold 2 values;
- a diagonal cell holds u and v in 1 LHS lane, which would put 2 tuples in 1 LHS lane on each axis;
- a tile that the size below uses would hold 2 base tuples.

Besides the weighted constraint that keeps the dummy rotational sibling tuple and the size below (`solve`), the solve's
constraints are:

- 1 per free lane, which allows at most 1 new base tuple whose u or v lies in that lane; the number of selected
  candidates, max-div's `k`, then forces every free lane to be used;
- 1 per free tile, which requires exactly 1 new base tuple in that tile.

max-div starts from a random selection that meets these constraints: the assignment of LHS lanes to tiles
(`_assign_lhs_lanes_to_tiles`) gives each free tile 1 free lane along u and 1 along v, and each tile takes a candidate
in the LHS cell of its 2 lanes (`MCTuplesPopulation.pick_or_draw_in_lhs_cells`).

After the solve, `MCTuplesSize.check_lhs_lanes_and_tiles` checks the size's tuples.
"""

import numpy as np
from max_div import Constraint

from sunnbear._core.benchmark.mc_tuples.core import MCTuplesSize
from sunnbear._core.utils.grouping import group_indices_by_id

from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation
from .rotations import tuple_array_of
from .solve import MCTuplesSolve, MCTuplesSolveSettings


# ==================================================================================================
#  MCTuplesSelectionSolve
# ==================================================================================================
class MCTuplesSelectionSolve(MCTuplesSolve):
    """`MCTuplesSelectionSolve` is the max-div solve that picks the new base tuples of 1 size from its population.

    Attributes:
        free_lanes: The size's lower-half LHS lanes that hold no value of the size below's base tuples, ascending.
        free_tiles: The size's lower-half tiles that hold no base tuple of the size below, ascending.
    """

    def __init__(
        self,
        n_population: int,
        required_base_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Draw the population from `n_population` candidates in the free lanes and tiles, then a starting selection.

        The starting selection adds a candidate to the population in each LHS cell that the starting selection needs and
        that holds no candidate, so the starting selection never runs out of candidates. Both draws advance
        `settings.rng`.
        """
        required_u, required_v = required_base_tuple_array[:, 0], required_base_tuple_array[:, 1]
        occupied_lanes = size.lhs_lane_indices(required_base_tuple_array.ravel())
        self.free_lanes = np.setdiff1d(np.arange(size.n_lower_half_lhs_lanes), occupied_lanes)
        self.free_tiles = np.setdiff1d(size.lower_half_tile_indices, size.tile_indices(required_u, required_v))
        population = MCTuplesPopulation.draw_in_off_diagonal_cells(
            n_population, self.free_lanes, self.free_tiles, size, settings.rng
        )
        u_lanes, v_lanes = self._assign_lhs_lanes_to_tiles(self.free_lanes, self.free_tiles, size, settings.rng)
        population, self._initial_new_selection_indices = population.pick_or_draw_in_lhs_cells(
            u_lanes, v_lanes, size, settings.rng
        )
        super().__init__(population, required_base_tuple_array, size, settings)

    @staticmethod
    def work_of(n_population: int, size: MCTuplesSize) -> int:
        """Return the solve's number of candidates times its number of selected candidates, both in base tuples.

        The candidates are the dummy rotational sibling tuple, the size below's base tuples and the population before
        its candidates in diagonal cells and in tiles that the size below's base tuples fill are dropped.
        """
        return (1 + size.n_required // 4 + n_population) * (1 + size // 4)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_base_tuple_constraints(self) -> list[Constraint]:
        """Return the constraints of the free lanes, then those of the free tiles.

        The constraint of a free lane allows at most 1 new base tuple with its u or its v in that lane; the constraint
        of a free tile requires exactly 1 new base tuple in that tile.
        """
        u, v = self.population.u, self.population.v
        lanes = self.size.lhs_lane_indices(np.concatenate([u, v]))
        candidates_of_values = self.n_always_selected_candidates + np.tile(np.arange(u.size), 2)
        lane_constraints = [
            Constraint(int_set=set(candidates_of_values[group].tolist()), min_count=0, max_count=1)
            for group in group_indices_by_id(lanes)
        ]
        tile_constraints = [
            Constraint(int_set=set((self.n_always_selected_candidates + group).tolist()), min_count=1, max_count=1)
            for group in group_indices_by_id(self.size.tile_indices(u, v))
        ]
        return lane_constraints + tile_constraints

    def _initial_new_selection(self) -> np.ndarray:
        """Return the random starting selection that the constructor drew, as indices into the population, ascending."""
        return self._initial_new_selection_indices

    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if the size's tuples break `MCTuplesSize.check_lhs_lanes_and_tiles`."""
        base_tuple_array = np.vstack([self.required_base_tuple_array, self.population.base_tuple_array[new_selection]])
        try:
            self.size.check_lhs_lanes_and_tiles(tuple_array_of(base_tuple_array))
        except ValueError as error:
            raise MCTuplesConstructionError(f"Size {self.size}: {error}") from error

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _assign_lhs_lanes_to_tiles(
        free_lanes: np.ndarray, free_tiles: np.ndarray, size: MCTuplesSize, rng: np.random.Generator
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return a free lane along u and one along v for each free tile, assigned at random, each free lane to 1 tile.

        The tuple of a tile has its u value in the tile's column and its v value in the tile's row, so the tile's u lane
        comes from the LHS lanes under its tile column, and its v lane from those under its tile row.

        LHS lanes are numbered the same way along u and v, so the lanes under tile column `b` and under tile row `b` are
        1 block of `size / n_tiles_per_axis` LHS lanes.

        Each block holds exactly as many free lanes as the free tiles in its tile column and its tile row need: every
        base tuple of the size below that fills a tile of that tile column or tile row fills 1 lane of the block too.

        Returns:
            The lanes along u and the lanes along v, both in the order of `free_tiles`.
        """
        tile_columns, tile_rows = size.tile_columns_and_rows(free_tiles)
        block_indices = size.tile_columns_of_lhs_lanes(free_lanes)
        u_lanes = np.empty(free_tiles.size, dtype=np.int64)
        v_lanes = np.empty(free_tiles.size, dtype=np.int64)
        for block in range(size.n_tiles_per_axis // 2):
            # The block's free lanes go in random order first to the free tiles in tile column `block`, as their u
            # lanes, then to the free tiles in tile row `block`, as their v lanes; the tile on the diagonal, in both,
            # takes 2 distinct lanes of the block.
            lanes = rng.permutation(free_lanes[block_indices == block])
            free_tile_positions_in_block_column = np.flatnonzero(tile_columns == block)
            free_tile_positions_in_block_row = np.flatnonzero(tile_rows == block)
            u_lanes[free_tile_positions_in_block_column] = lanes[: free_tile_positions_in_block_column.size]
            v_lanes[free_tile_positions_in_block_row] = lanes[free_tile_positions_in_block_column.size :]
        return u_lanes, v_lanes
