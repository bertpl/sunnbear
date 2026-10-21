"""This module combines the automatic statuses with the decisions into each row's final status."""

from .data_files import DECIDED_STATUSES, UNDECIDED, AutomaticStatus, FinalStatus, join_row_ids


def decide_final_statuses(
    automatic_statuses: dict[str, AutomaticStatus], decisions: dict[str, FinalStatus]
) -> dict[str, FinalStatus]:
    """Return the final status of each row, keyed by row id, for rows given in time order.

    A row's decision overrides its automatic status; a row with neither a decision nor a decided automatic status
    stays `undecided`.

    Then a row that names a duplicate names that duplicate's own earlier row instead, so that each row names the
    first appearance of its function; a row that names a variant or an extended row keeps naming it, since that row
    is the first appearance of its constants or parameter values.
    """
    final_statuses = {}
    for row_id, automatic in automatic_statuses.items():
        if row_id in decisions:
            final_statuses[row_id] = decisions[row_id]
        else:
            final_statuses[row_id] = FinalStatus.from_automatic_status(automatic)
    # the rows come in time order, so each row's earlier rows already name their own first appearances
    for row_id, final in final_statuses.items():
        first_appearances = [_first_appearance(row_id, earlier, final_statuses) for earlier in final.earlier_row_ids]
        final_statuses[row_id] = FinalStatus(final.status, join_row_ids(first_appearances), final.reason)
    return final_statuses


def find_problems(final_statuses: dict[str, FinalStatus], decisions: dict[str, FinalStatus]) -> list[str]:
    """Return the problems of the final statuses, for rows given in time order; an empty list if there are none.

    A problem is a decision for an unknown row, a row that names an unknown or a later row, an undecided row, a row
    with an unknown status, or a row that is not new and names no earlier row.
    """
    position = {row_id: i for i, row_id in enumerate(final_statuses)}
    problems = [f"decisions.csv names an unknown row, {row_id}" for row_id in decisions if row_id not in position]
    for row_id, final in final_statuses.items():
        for earlier in final.earlier_row_ids:
            if earlier not in position:
                problems.append(f"{row_id} names an unknown row, {earlier}")
            elif position[earlier] >= position[row_id]:
                problems.append(f"{row_id} names a row that is not earlier, {earlier}")
        if final.status == UNDECIDED:
            problems.append(f"{row_id} needs a decision in decisions.csv")
        elif final.status not in DECIDED_STATUSES:
            problems.append(f"{row_id} has an unknown status, {final.status}")
        elif final.status != "new" and not final.earlier_rows:
            problems.append(f"{row_id} is {final.status} but names no earlier row")
    return problems


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _first_appearance(row_id: str, earlier_row_id: str, final_statuses: dict[str, FinalStatus]) -> str:
    """Return the last row of the chain of duplicates from `earlier_row_id`, stopping at a cycle.

    `row_id` is the row that names `earlier_row_id`; the walk also stops where the chain leads back to it.
    """
    seen = {row_id}
    while (
        earlier_row_id in final_statuses
        and final_statuses[earlier_row_id].status == "duplicate"
        and earlier_row_id not in seen
    ):
        seen.add(earlier_row_id)
        next_ids = final_statuses[earlier_row_id].earlier_row_ids
        earlier_row_id = next_ids[0] if next_ids else ""
    return earlier_row_id
