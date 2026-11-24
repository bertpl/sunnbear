"""`FormulaRegistry.publication_of` finds a publication for each shipped formula of category 1, and each shipped
publication holds a valid CSL-JSON item with a title and a year.

In category 1, the published test problems, each category of a subcategory other than 1.99 holds the formulas of 1
publication and declares that publication. The formulas of subcategory 1.99 modify published formulas, and come from the
publications of the formulas that they modify.

Each test checks every shipped formula or category in 1 test, and lists the ones that fail; the checks are cheap, so 1
test item per formula or category would only add items.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import jsonschema

import sunnbear._core.problems.catalog as catalog
from sunnbear._core.problems.core import FormulaRegistry

_CATALOG_PREFIX = f"{catalog.__name__}."
_SHIPPED_FORMULAS = [
    formula for formula in FormulaRegistry.formulas() if type(formula).__module__.startswith(_CATALOG_PREFIX)
]
_SHIPPED_CATEGORIES = [
    category for category in FormulaRegistry.categories() if type(category).__module__.startswith(_CATALOG_PREFIX)
]
# The published JSON schema of CSL-JSON; csl_schema/README.md names its source.
_CSL_DATA_SCHEMA_PATH = Path(__file__).parent / "csl_schema" / "csl-data.json"
_SINGLE_PUBLICATION_CATEGORIES = [
    category
    for category in _SHIPPED_CATEGORIES
    if len(category.number) == 3 and category.number[0] == 1 and category.number[1] != 99
]


def test_exactly_the_single_publication_categories_declare_their_publication():
    """A category of a subcategory of category 1 other than 1.99 declares its publication; no other category does."""
    # --- act --------------------------
    categories_without_publication = [
        category.label for category in _SINGLE_PUBLICATION_CATEGORIES if category.publication is None
    ]
    other_categories_with_publication = [
        category.label
        for category in _SHIPPED_CATEGORIES
        if category not in _SINGLE_PUBLICATION_CATEGORIES and category.publication is not None
    ]

    # --- assert -----------------------
    assert _SINGLE_PUBLICATION_CATEGORIES
    assert categories_without_publication == []
    assert other_categories_with_publication == []


def test_exactly_the_formulas_of_category_1_come_from_a_publication():
    """A formula of category 1 has a publication and a location in it; no other shipped formula has both."""
    # --- act --------------------------
    failing = []
    for formula in _SHIPPED_FORMULAS:
        is_in_category_1 = formula.number[0] == 1
        has_publication = FormulaRegistry.publication_of(formula) is not None
        has_location_in_publication = formula.location_in_publication is not None
        if is_in_category_1 != (has_publication and has_location_in_publication):
            failing.append(formula.label)

    # --- assert -----------------------
    assert failing == []


def test_citation_keys_are_unique():
    """No 2 shipped publications declare the same citation key."""
    # --- act --------------------------
    keys = [category.publication.citation_key for category in _SINGLE_PUBLICATION_CATEGORIES]
    counts = Counter(key for key in keys if key is not None)

    # --- assert -----------------------
    assert [key for key, count in counts.items() if count > 1] == []


def test_publications_declare_their_title_and_year():
    """A shipped publication's item has a title and a year, and its category's name ends in that year."""
    # --- act --------------------------
    failing = []
    for category in _SINGLE_PUBLICATION_CATEGORIES:
        publication = category.publication
        has_title = bool(publication.csl_item.get("title"))
        is_category_named_with_its_year = category.name.endswith(f"({publication.year})")
        if not has_title or not is_category_named_with_its_year:
            failing.append(category.label)

    # --- assert -----------------------
    assert failing == []


def test_publications_are_valid_csl_json_items():
    """Every shipped publication's item is valid against the published CSL-JSON schema.

    A consumer that renders a citation ignores a field that it does not know, so a misspelled field would leave a part
    of the citation out without an error; the schema allows no field that it does not define.
    """
    # --- arrange ----------------------
    schema = json.loads(_CSL_DATA_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)

    # --- act --------------------------
    items = [category.publication.csl_item for category in _SINGLE_PUBLICATION_CATEGORIES]
    errors = [f"{error.path}: {error.message}" for error in validator.iter_errors(items)]

    # --- assert -----------------------
    assert errors == []


def test_formula_names_are_readable_and_unique_within_each_single_publication_category():
    """Each single-publication category holds formulas, no 2 of them share a name, and each starts with a capital."""
    # --- act --------------------------
    names_by_category = defaultdict(list)
    for formula in _SHIPPED_FORMULAS:
        category = FormulaRegistry.category_of(formula)
        if category in _SINGLE_PUBLICATION_CATEGORIES:
            names_by_category[category.label].append(formula.name)
    duplicates = [
        f"{label}: {name}"
        for label, names in names_by_category.items()
        for name, count in Counter(names).items()
        if count > 1
    ]
    not_readable = [name for names in names_by_category.values() for name in names if not re.match(r"[A-Z][a-z]", name)]

    # --- assert -----------------------
    assert len(names_by_category) == len(_SINGLE_PUBLICATION_CATEGORIES)
    assert duplicates == []
    assert not_readable == []
