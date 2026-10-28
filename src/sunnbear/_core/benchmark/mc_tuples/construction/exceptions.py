"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class MCTuplesConstructionError(SunnbearError):
    """`MCTuplesConstructionError` is raised when `generate_mc_tuples` cannot build a size that meets its constraints.

    - the population runs out of candidates before the random starting selection, with at most 1 new value per lower
      fine lane, holds the size's new base tuples;
    - the selection misses the dummy rotational sibling tuple or a base tuple of the size below;
    - a lower fine lane holds 2 or more values of new base tuples after the selection solve;
    - a fine cell of a new base tuple does not hold exactly 1 new base tuple after the refinement solve.
    """
