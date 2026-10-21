"""Build `rows.csv`, `summary.md` and `timeline.html` of `data/literature_test_problems/` from its inputs.

Run from the repo root with `uv run python -m scripts.literature_test_problems`. The script writes all 3 files,
then prints the counts per status and every problem that it found, such as a row that needs a decision; it exits
with status 1 if there is a problem.
"""

import sys
from collections import Counter

from .data_files import DataFolder, RowStatus, read_decisions, read_sources, write_rows_table
from .matching import compute_automatic_statuses
from .overview import Overview
from .statuses import decide_final_statuses, find_problems


def main() -> int:
    """Build the 3 generated files, and return the exit status."""
    folder = DataFolder.in_repo()
    sources = read_sources(folder.sources_dir)
    decisions = read_decisions(folder.decisions_file)
    # --- statuses stage -------------------------
    automatic = compute_automatic_statuses([row for source in sources for row in source.rows])
    final = decide_final_statuses(automatic, decisions)
    rows = [
        RowStatus.from_source_row(source, row, automatic[row.row_id], final[row.row_id])
        for source in sources
        for row in source.rows
    ]
    write_rows_table(folder.rows_file, rows)
    # --- overview stage -------------------------
    overview = Overview.build(sources, rows)
    folder.summary_file.write_text(overview.summary_markdown(), encoding="utf-8")
    folder.timeline_file.write_text(overview.timeline_page(), encoding="utf-8")
    # --- report ---------------------------------
    print(f"{len(sources)} sources, {len(rows)} rows")
    print("automatic status:", dict(Counter(row.automatic.status for row in rows).most_common()))
    print("final status:", dict(Counter(row.final.status for row in rows).most_common()))
    problems = find_problems(final, decisions)
    for problem in problems:
        print(f"problem: {problem}")
    if problems:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
