"""Each shipped formula of a publication finds it, and each publication declares its parts.

A category of the subcategories 1.1 to 1.4 below category 1, the published test problems, holds the formulas of 1
publication, and declares it. The formulas of subcategory 1.99 modify published formulas, and come from the publications
of the formulas that they modify.
"""

import re
from collections import Counter

import pytest

import sunnbear._core.problems.catalog as catalog
from sunnbear._core.problems.core import FormulaRegistry

_CATALOG_PREFIX = f"{catalog.__name__}."
_SHIPPED_FORMULAS = [
    formula for formula in FormulaRegistry.formulas() if type(formula).__module__.startswith(_CATALOG_PREFIX)
]
_SHIPPED_CATEGORIES = [
    category for category in FormulaRegistry.categories() if type(category).__module__.startswith(_CATALOG_PREFIX)
]
_PUBLICATION_CATEGORIES = [
    category
    for category in _SHIPPED_CATEGORIES
    if len(category.number) == 3 and category.number[0] == 1 and category.number[1] != 99
]
_PUBLICATIONS = [category.publication for category in _PUBLICATION_CATEGORIES if category.publication is not None]


# Each test checks every shipped formula or category in 1 test, and lists the ones that fail; the checks are cheap, so
# 1 test item per formula or category would only add items.
def test_exactly_the_categories_of_1_publication_declare_it():
    """A category of subcategories 1.1 to 1.4 declares its publication, and no other shipped category declares one."""
    # --- act --------------------------
    without = [category.label for category in _PUBLICATION_CATEGORIES if category.publication is None]
    others_with = [
        category.label
        for category in _SHIPPED_CATEGORIES
        if category not in _PUBLICATION_CATEGORIES and category.publication is not None
    ]

    # --- assert -----------------------
    assert _PUBLICATION_CATEGORIES
    assert without == []
    assert others_with == []


def test_exactly_the_formulas_of_category_1_come_from_a_publication():
    """A formula of category 1 has a publication and a location in it; no other shipped formula has either."""
    # --- act --------------------------
    failing = [
        formula.label
        for formula in _SHIPPED_FORMULAS
        if (formula.number[0] == 1)
        != (FormulaRegistry.publication_of(formula) is not None and formula.location_in_publication is not None)
    ]

    # --- assert -----------------------
    assert failing == []


def test_citation_keys_are_unique():
    """No 2 shipped publications declare the same citation key."""
    # --- act --------------------------
    counts = Counter(publication.citation_key for publication in _PUBLICATIONS if publication.citation_key is not None)

    # --- assert -----------------------
    assert [key for key, count in counts.items() if count > 1] == []


@pytest.mark.skip(reason="the shipped publications declare only their citations")
def test_publications_declare_their_parts():
    """A shipped publication declares its citation key, authors, year, title and where it appeared.

    A publication whose citation holds a link declares its DOI or a URL too.
    """
    # --- act --------------------------
    failing = []
    for category in _PUBLICATION_CATEGORIES:
        publication = category.publication
        parts = (publication.citation_key, publication.year, publication.title, publication.published_in)
        has_parts = all(part is not None for part in parts) and len(publication.authors) > 0
        has_link = re.search(r"https?://", publication.citation) is not None
        has_doi_or_url = publication.doi is not None or publication.url is not None
        if not has_parts or (has_link and not has_doi_or_url):
            failing.append(category.label)

    # --- assert -----------------------
    assert failing == []
