"""This package builds the generated files of `data/literature_test_problems/` from its source files and decisions.

Run it from the repo root:

    uv run python -m scripts.literature_test_problems

It runs in 2 stages:

- **Statuses** (`matching`, `statuses`; needs sympy): compare every row with all earlier rows, apply
  `decisions.csv`, and write `rows.csv`.
- **Overview** (`overview`; standard library only): write `summary.md` and `timeline.html` from `rows.csv` and the
  source files.

The folder's README gives the format of each file and the rules that decide a row's status.
"""
