"""Build the generated files of `data/literature_test_problems/` from its source files and decisions.

Run from the repo root with `uv run python -m scripts.literature_test_problems`. The script:

- writes every generated file;
- prints the counts per status, the number of formulas, and every problem that it found, such as a row that needs a
  decision;
- exits with status 1 if there is a problem.
"""

import sys
from collections import Counter

from .data_files import (
    DataFolder,
    FormulaDecision,
    RowsTableLine,
    read_decisions,
    read_formula_decisions,
    read_sources,
    write_rows_table,
)
from .formulas import FormulasTable
from .matching import EarlierRowIndex
from .overview import Overview
from .statuses import decide_final_statuses, find_problems


def main() -> int:
    """Build the generated files, and return the exit status."""
    folder = DataFolder.in_repo()
    sources = read_sources(folder.sources_dir)
    decisions = read_decisions(folder.decisions_file)
    formula_decisions = read_formula_decisions(folder.formula_decisions_file)
    # --- statuses stage -------------------------
    automatic_statuses = EarlierRowIndex.compute_automatic_statuses(
        [row for source in sources for row in source.rows], decisions
    )
    final_statuses = decide_final_statuses(automatic_statuses, decisions)
    rows = [
        RowsTableLine.from_source_row(source, row, automatic_statuses[row.row_id], final_statuses[row.row_id])
        for source in sources
        for row in source.rows
    ]
    write_rows_table(folder.rows_file, rows)
    # --- overview stage -------------------------
    overview = Overview.build(sources, rows)
    folder.summary_file.write_text(overview.summary_markdown(), encoding="utf-8")
    folder.timeline_file.write_text(overview.timeline_html(), encoding="utf-8")
    # --- formulas stage -------------------------
    formulas_table = FormulasTable.build(rows, formula_decisions)
    folder.formulas_file.write_text(formulas_table.csv_text(), encoding="utf-8")
    # --- report ---------------------------------
    print(f"{len(sources)} sources, {len(rows)} rows")
    print("automatic status:", dict(Counter(row.automatic_status.status for row in rows).most_common()))
    print("final status:", dict(Counter(row.final_status.status for row in rows).most_common()))
    print(f"{len(formulas_table.formulas)} formulas")
    problems = find_problems(final_statuses, decisions)
    problems += FormulaDecision.find_all_problems(formula_decisions, rows)
    for problem in problems:
        print(f"problem: {problem}")
    if problems:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
