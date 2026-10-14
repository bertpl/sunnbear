"""This package holds the solver framework: the base classes in `core`, the shipped solvers in families beside `core`.

Each family, such as `bracketing`, imports from `core` only.

The implementation principles of the solvers, which decide how each solver implements its published method, are in
``IMPLEMENTATION_PRINCIPLES.md`` beside this file. The module docstring of each solver's ``solver.py`` records how the
principles shape that solver.
"""
