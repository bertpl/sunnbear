"""Formula catalog: concrete `Formula` implementations, one module per formula.

Layout convention: one subpackage per number block (e.g. ``f1xx_polynomials``),
one module per formula number (e.g. ``f101_cubic``), one `Formula` subclass
per module. Modules here are auto-imported by the registry, so adding a
formula is adding a file — no list or import to maintain.
"""
