"""This package holds the shipped formulas and their categories, one folder per category.

Layout convention, checked by the catalog tests:

- a category is a package ``c<NN>_<slug>/`` whose ``__init__.py`` defines one `FormulaCategory`
  subclass and imports the package's modules and subpackages
- a formula is a module ``f<NN>_<slug>.py`` defining one `Formula` subclass
- ``<NN>`` is the last element of the category's or formula's number, zero-padded to 2 digits, and ``<slug>`` is its
  ``name_slug``; the folder path therefore reads as the full number, e.g.
  ``c02_documented_functions/c01_polynomials/f01_cubic.py`` is formula ``2.1.1``

Importing this package registers every shipped formula and category.
"""

from . import c01_existing_benchmark_suites, c02_documented_functions, c03_custom_functions, c99_user_defined
