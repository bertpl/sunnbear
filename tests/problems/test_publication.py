import pytest

from sunnbear._core.problems.core import Publication

_CITATION = (
    "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of an equation. BIT 11(2), "
    "168-174. https://doi.org/10.1007/BF01934364."
)
_PARTS = {
    "citation_key": "Dowell71",
    "authors": ("Dowell, M.", "Jarratt, P."),
    "year": 1971,
    "title": "A modified regula falsi method for computing the root of an equation",
    "published_in": "BIT",
    "doi": "10.1007/BF01934364",
}


def test_publication_whose_citation_holds_its_parts_is_accepted():
    """A publication whose citation holds each of its declared parts is built."""
    # --- act --------------------------
    publication = Publication(citation=_CITATION, **_PARTS)

    # --- assert -----------------------
    assert publication.citation_key == "Dowell71"


@pytest.mark.parametrize(
    "parts",
    [
        {"authors": ("Dowell, M.", "Jarrat, P.")},
        {"year": 1972},
        {"title": "A modified regula falsi method for finding a root"},
        {"published_in": "BIT Numerical Mathematics"},
        {"doi": "10.1007/BF01934365"},
        {"url": "https://link.springer.com/article/10.1007/BF01934364"},
    ],
)
def test_publication_with_a_part_that_its_citation_does_not_hold_is_rejected(parts):
    """A declared part that the citation does not hold, such as a misspelled author, is rejected when it is built."""
    with pytest.raises(ValueError, match="does not hold"):
        Publication(citation=_CITATION, **parts)


@pytest.mark.parametrize("citation_key", ["Dowell71", "Ganchovski26a", "RootsFortran25"])
def test_citation_key_of_a_name_and_2_digits_is_accepted(citation_key):
    """A citation key is a capitalized name, the year's last 2 digits, and an optional lowercase letter."""
    # --- act --------------------------
    publication = Publication(citation=_CITATION, citation_key=citation_key)

    # --- assert -----------------------
    assert publication.citation_key == citation_key


@pytest.mark.parametrize("citation_key", ["dowell71", "Dowell1971", "Dowell71ab", "Dowell", "Dowell 71"])
def test_citation_key_of_another_form_is_rejected(citation_key):
    """A citation key that is not a capitalized name, 2 digits and an optional letter is rejected."""
    with pytest.raises(ValueError, match="citation key"):
        Publication(citation=_CITATION, citation_key=citation_key)


def test_citation_key_that_does_not_end_in_the_year_is_rejected():
    """A citation key whose 2 digits are not the last 2 digits of the publication's year is rejected."""
    with pytest.raises(ValueError, match="does not end in the last 2 digits"):
        Publication(citation=_CITATION, citation_key="Dowell72", year=1971)
