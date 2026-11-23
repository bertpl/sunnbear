"""`FormulaRegistry.publication_of` finds a publication for each shipped formula of category 1, and each shipped
publication declares its parts.

In category 1, the published test problems, each category of a subcategory other than 1.99 holds the formulas of 1
publication and declares that publication. The formulas of subcategory 1.99 modify published formulas, and come from the
publications of the formulas that they modify.

Each test checks every shipped formula or category in 1 test, and lists the ones that fail; the checks are cheap, so 1
test item per formula or category would only add items.
"""

import re
from collections import Counter, defaultdict

import sunnbear._core.problems.catalog as catalog
from sunnbear._core.problems.core import FormulaRegistry

_CATALOG_PREFIX = f"{catalog.__name__}."
_SHIPPED_FORMULAS = [
    formula for formula in FormulaRegistry.formulas() if type(formula).__module__.startswith(_CATALOG_PREFIX)
]
_SHIPPED_CATEGORIES = [
    category for category in FormulaRegistry.categories() if type(category).__module__.startswith(_CATALOG_PREFIX)
]
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


def test_citations_are_1_paragraph():
    """A shipped publication's citation is 1 paragraph: the citation alone, without notes on how the rows were taken."""
    # --- act --------------------------
    failing = [category.label for category in _SINGLE_PUBLICATION_CATEGORIES if "\n" in category.publication.citation]

    # --- assert -----------------------
    assert failing == []


def test_publications_declare_their_parts():
    """A shipped publication declares its citation key, its title, a DOI or URL, and the year in its category's name.

    A category's name ends in its publication's year, such as "Brent (1973)". Only a publication whose citation holds a
    link has a DOI or URL to declare; a book cited by its ISBN has neither. The test does not require the authors or
    where the publication appeared, because some citations name neither, such as that of a code repository.
    """
    # --- act --------------------------
    failing = []
    for category in _SINGLE_PUBLICATION_CATEGORIES:
        publication = category.publication
        has_key_and_title = publication.citation_key is not None and publication.title is not None
        is_category_named_with_its_year = category.name.endswith(f"({publication.year})")
        has_link = re.search(r"https?://", publication.citation) is not None
        has_doi_or_url = publication.doi is not None or publication.url is not None
        if not has_key_and_title or not is_category_named_with_its_year or (has_link and not has_doi_or_url):
            failing.append(category.label)

    # --- assert -----------------------
    assert failing == []


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
