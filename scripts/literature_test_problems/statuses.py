"""This module combines the automatic statuses with the decisions into each row's final status."""

from .data_files import FINAL_STATUSES, ROW_ID_SEPARATOR, UNDECIDED, AutomaticStatus, FinalStatus


def decide_final_statuses(
    automatic: dict[str, AutomaticStatus], decisions: dict[str, FinalStatus]
) -> dict[str, FinalStatus]:
    """Return the final status of each row, keyed by row id, for rows given in time order.

    A row's decision wins over its automatic status; a row with neither a decision nor a decided automatic status
    stays `judge`. Then a row that names a duplicate names that duplicate's own earlier row instead, so that every
    chain ends at the first appearance; a variant or an extended row stays named, since it is the first appearance
    of its constants or parameter values.
    """
    final = {}
    for row_id, status in automatic.items():
        if row_id in decisions:
            final[row_id] = decisions[row_id]
        elif status.status == "new":
            final[row_id] = FinalStatus("new", "", "")
        elif status.status != UNDECIDED:
            final[row_id] = FinalStatus(status.status, status.matches, "")
        else:
            final[row_id] = FinalStatus(UNDECIDED, "", "")
    # the rows come in time order, so each row's earlier rows already name their own first appearances
    for row_id, status in final.items():
        resolved = [_first_appearance(row_id, earlier, final) for earlier in status.earlier_row_ids]
        earlier_rows = ROW_ID_SEPARATOR.join(dict.fromkeys(r for r in resolved if r))
        final[row_id] = FinalStatus(status.status, earlier_rows, status.reason)
    return final


def find_problems(final: dict[str, FinalStatus], decisions: dict[str, FinalStatus]) -> list[str]:
    """Return the problems of the final statuses, for rows given in time order; an empty list if there are none.

    A problem is a decision for an unknown row, a row that names an unknown or a later row, an undecided row, or a
    row that is not new and names no earlier row.
    """
    position = {row_id: i for i, row_id in enumerate(final)}
    problems = [f"decisions.csv names an unknown row, {row_id}" for row_id in decisions if row_id not in position]
    for row_id, status in final.items():
        for earlier in status.earlier_row_ids:
            if earlier not in position:
                problems.append(f"{row_id} names an unknown row, {earlier}")
            elif position[earlier] >= position[row_id]:
                problems.append(f"{row_id} names a row that is not earlier, {earlier}")
        if status.status == UNDECIDED:
            problems.append(f"{row_id} needs a decision in decisions.csv")
        elif status.status not in FINAL_STATUSES:
            problems.append(f"{row_id} has an unknown status, {status.status}")
        elif status.status != "new" and not status.earlier_rows:
            problems.append(f"{row_id} is {status.status} but names no earlier row")
    return problems


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _first_appearance(row_id: str, earlier: str, final: dict[str, FinalStatus]) -> str:
    """Return the row that a chain of duplicates from `earlier` ends at, stopping at a cycle."""
    seen = {row_id}
    while earlier in final and final[earlier].status == "duplicate" and earlier not in seen:
        seen.add(earlier)
        earlier = final[earlier].earlier_row_ids[0] if final[earlier].earlier_row_ids else ""
    return earlier
