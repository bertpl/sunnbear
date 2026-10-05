"""`Illinois` implements the Illinois method: regula falsi that halves the function value at a bound it keeps again."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound, SolveState


# ==================================================================================================
#  IllinoisState
# ==================================================================================================
@dataclass
class IllinoisState(SolveState):
    """`IllinoisState` adds the 2 values that the Illinois method carries from one iteration to the next.

    Attributes:
        iterate_bound: The bound that holds the most recent iterate. Before the first iterate, the upper bound
            plays that role, as in the published method.
        retained_f: The function value that the chord uses at the other bound, the retained one: that bound's own
            value, halved once for every iteration that kept it again.
    """

    iterate_bound: IntervalBound = IntervalBound.UPPER
    retained_f: float = field(init=False)

    def __post_init__(self) -> None:
        """Start with the lower bound as the retained bound, at its own function value."""
        self.retained_f = self.interval.fa


# ==================================================================================================
#  Illinois
# ==================================================================================================
class Illinois(BracketingSolver[IllinoisState]):
    """`Illinois` evaluates where the chord through the bound points crosses zero, as regula falsi does, but halves
    the function value of a bound that the interval keeps twice in a row.

    Regula falsi stalls when the function is convex or concave on the interval: it keeps 1 bound forever, so the
    interval never shrinks below the distance from that bound to the root. The Illinois method (Dowell and
    Jarratt, BIT 11, 1971) avoids the stall:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is halved before the next chord is drawn, which moves the next iterate toward the retained bound;
    - each further iteration that keeps that bound halves its value again;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, at its own
      function value.

    The chord formula is regula falsi's, as Ford (Scientia Iranica 4, 1997) states the modified step, so the
    Illinois method differs from `RegulaFalsi` only in the function value that it uses at the retained bound.
    """

    name = "illinois"
    version = 1
    state_cls = IllinoisState

    def _next_x(self, state: IllinoisState, interval: Interval) -> float:
        """Return where the chord crosses zero, with the retained bound's function value halved as described above."""
        # --- update the retained bound's value ------
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is halved.
        elif replaced_bound is state.iterate_bound:
            # The new iterate replaced the previous iterate, so the retained bound was kept once more.
            state.retained_f = 0.5 * state.retained_f
        else:
            # The new iterate replaced the retained bound, so the previous iterate is the retained bound from now on.
            state.retained_f = interval.fb if replaced_bound is IntervalBound.LOWER else interval.fa
            state.iterate_bound = replaced_bound

        # --- regula falsi's chord -------------------
        if state.iterate_bound is IntervalBound.UPPER:
            fa, fb = state.retained_f, interval.fb
        else:
            fa, fb = interval.fa, state.retained_f
        return (interval.a * fb - interval.b * fa) / (fb - fa)
