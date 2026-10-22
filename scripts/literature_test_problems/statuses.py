"""This module combines the automatic statuses with the decisions into each row's final status."""

from .data_files import AutomaticStatus, FinalStatus


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
        resolved_statuses[row_id] = final.with_first_appearances(resolved_statuses)
    return resolved_statuses


def find_problems(final_statuses: dict[str, FinalStatus], decisions: dict[str, FinalStatus]) -> list[str]:
    """Return the problems of the final statuses, for rows given in time order; an empty list if there are none.

    A problem is a decision for an unknown row, a problem of the rows that a row names
    (`FinalStatus.find_named_row_problems`), or a problem of a row's status and its fields
    (`FinalStatus.find_status_problems`).
    """
    position = {row_id: i for i, row_id in enumerate(final_statuses)}
    problems = [f"decisions.csv names an unknown row, {row_id}" for row_id in decisions if row_id not in position]
    for row_id, final in final_statuses.items():
        problems += final.find_named_row_problems(row_id, final_statuses, position)
        problems += final.find_status_problems(row_id)
    return problems
