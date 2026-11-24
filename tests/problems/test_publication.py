import json

import pytest

from sunnbear._core.problems.core import Publication

_ITEM = {
    "id": "Dowell71",
    "type": "article-journal",
    "author": [{"family": "Dowell", "given": "M."}, {"family": "Jarratt", "given": "P."}],
    "title": "A modified regula falsi method for computing the root of an equation",
    "container-title": "BIT",
    "issued": {"date-parts": [[1971, 6]]},
    "DOI": "10.1007/BF01934364",
}


def test_publication_gives_its_citation_key_and_year():
    """A publication's citation key is its item's ``id``, and its year is the year of the item's ``issued``."""
    # --- act --------------------------
    publication = Publication(csl_item=_ITEM)

    # --- assert -----------------------
    assert (publication.citation_key, publication.year) == ("Dowell71", 1971)


def test_year_of_an_item_without_date_of_issue_is_the_year_of_access():
    """An item without ``issued``, such as an unversioned web page, takes its year from ``accessed``."""
    # --- arrange ----------------------
    item = {"id": "Borchers26", "type": "webpage", "title": "Root Finding", "accessed": {"date-parts": [[2026, 10]]}}

    # --- act --------------------------
    publication = Publication(csl_item=item)

    # --- assert -----------------------
    assert publication.year == 2026


@pytest.mark.parametrize("citation_key", ["Dowell71", "Ganchovski71a", "RootsFortran71"])
def test_citation_key_of_a_name_and_2_digits_is_accepted(citation_key):
    """A citation key is a capitalized name, the year's last 2 digits, and an optional lowercase letter."""
    # --- act --------------------------
    publication = Publication(csl_item={**_ITEM, "id": citation_key})

    # --- assert -----------------------
    assert publication.citation_key == citation_key


@pytest.mark.parametrize("citation_key", ["dowell71", "Dowell1971", "Dowell71ab", "Dowell", "Dowell 71"])
def test_citation_key_of_another_form_is_rejected(citation_key):
    """A citation key that is not a capitalized name, 2 digits and an optional letter is rejected."""
    with pytest.raises(ValueError, match="citation key"):
        Publication(csl_item={**_ITEM, "id": citation_key})


def test_citation_key_that_does_not_end_in_the_year_is_rejected():
    """A citation key whose 2 digits are not the last 2 digits of the item's year is rejected."""
    with pytest.raises(ValueError, match="does not end in the last 2 digits"):
        Publication(csl_item={**_ITEM, "id": "Dowell72"})


def test_publication_is_built_from_its_csl_json_file(tmp_path):
    """`Publication.from_csl_json_file` builds the publication whose item a JSON file holds."""
    # --- arrange ----------------------
    path = tmp_path / "publication.csl.json"
    path.write_text(json.dumps(_ITEM), encoding="utf-8")

    # --- act --------------------------
    publication = Publication.from_csl_json_file(path)

    # --- assert -----------------------
    assert publication.csl_item == _ITEM
