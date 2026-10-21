"""This module combines the automatic statuses with the decisions into each row's final status."""

from .data_files import AutomaticStatus, FinalStatus, join_row_ids


def decide_final_statuses(
    automatic_statuses: dict[str, AutomaticStatus], decisions: dict[str, FinalStatus]
) -> dict[str, FinalStatus]:
    """Return the final status of each row, keyed by row id, for rows given in time order.

    A row's decision overrides its automatic status; a row with neither a decision nor a decided automatic status
    stays `undecided`.

    Then each earlier row that a row names in `duplicate_of` or `derived_from`, and that is itself a duplicate, is
    replaced by the rows in that duplicate's `duplicate_of`, so that each row names the first appearance of its
    function. A named row that is not earlier is left as it is, for `find_problems` to report.
    """
    final_statuses = {}
    for row_id, automatic in automatic_statuses.items():
        if row_id in decisions:
            final_statuses[row_id] = decisions[row_id]
        else:
            final_statuses[row_id] = FinalStatus.from_automatic_status(automatic)
    # the rows come in time order, so each earlier row already names its own first appearances
    resolved_statuses: dict[str, FinalStatus] = {}
    for row_id, final in final_statuses.items():
        resolved_statuses[row_id] = FinalStatus(
            final.status,
            join_row_ids(_first_appearances(final.duplicate_of_ids, resolved_statuses)),
            join_row_ids(_first_appearances(final.derived_from_ids, resolved_statuses)),
            final.reason,
        )
    return resolved_statuses


def find_problems(final_statuses: dict[str, FinalStatus], decisions: dict[str, FinalStatus]) -> list[str]:
    """Return the problems of the final statuses, for rows given in time order; an empty list if there are none.

    A problem is a decision for an unknown row, a row that names an unknown or a later row, an undecided row, a row
    with an unknown status, a duplicate that names no row in `duplicate_of`, names a row there that is not `new`, or
    names rows in `derived_from`, a row that is not a duplicate and names rows in `duplicate_of`, or an `incomplete`
    row without a reason.
    """
    position = {row_id: i for i, row_id in enumerate(final_statuses)}
    problems = [f"decisions.csv names an unknown row, {row_id}" for row_id in decisions if row_id not in position]
    for row_id, final in final_statuses.items():
        problems += _named_row_problems(row_id, final, final_statuses, position)
        problems += final.find_status_problems(row_id)
    return problems


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _named_row_problems(
    row_id: str, final: FinalStatus, final_statuses: dict[str, FinalStatus], position: dict[str, int]
) -> list[str]:
    """Return the problems of the rows that 1 row names: unknown, not earlier, or not `new` in `duplicate_of`."""
    problems = []
    for earlier in final.named_row_ids:
        if earlier not in position:
            problems.append(f"{row_id} names an unknown row, {earlier}")
        elif position[earlier] >= position[row_id]:
            problems.append(f"{row_id} names a row that is not earlier, {earlier}")
    for earlier in final.duplicate_of_ids:
        if earlier in final_statuses and final_statuses[earlier].status != "new":
            problems.append(f"{row_id} is a duplicate of a row that is not new, {earlier}")
    return problems


def _first_appearances(row_ids: list[str], resolved_statuses: dict[str, FinalStatus]) -> list[str]:
    """Return the row ids with each resolved duplicate replaced by the rows in its `duplicate_of`.

    `resolved_statuses` holds the final statuses of the earlier rows, which already name their own first appearances.
    """
    first_appearances = []
    for row_id in row_ids:
        if row_id in resolved_statuses and resolved_statuses[row_id].status == "duplicate":
            first_appearances.extend(resolved_statuses[row_id].duplicate_of_ids)
        else:
            first_appearances.append(row_id)
    return first_appearances
