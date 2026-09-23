"""The folder and file names of the formula catalog carry each node's number and name."""

import re

import pytest

import sunnbear._core.functions.catalog as catalog
from sunnbear._core.functions.core.taxonomy import FormulaTaxonomyNode
from sunnbear.functions import Formula, FormulaRegistry

_CATALOG_PREFIX = f"{catalog.__name__}."

# A catalog folder or file name is a letter (``c`` for a category, ``f`` for a formula), a 2-digit
# number and a slug.
_NAME_PATTERN = re.compile(r"(?P<kind>[cf])(?P<number>[0-9]{2})_(?P<slug>[a-z0-9_]+)")


def _catalog_nodes() -> list[FormulaTaxonomyNode]:
    """Return every registered category and formula whose class is defined inside the catalog."""
    nodes = [*FormulaRegistry.categories(), *FormulaRegistry.formulas()]
    return [node for node in nodes if type(node).__module__.startswith(_CATALOG_PREFIX)]


@pytest.mark.parametrize("node", _catalog_nodes(), ids=lambda node: type(node).__name__)
def test_catalog_path_matches_number_and_names(node):
    """Each part of the module path is ``c<NN>_<slug>`` (a category) or ``f<NN>_<slug>`` (the formula itself)."""
    # --- arrange ----------------------
    parts = type(node).__module__.removeprefix(_CATALOG_PREFIX).split(".")
    categories = {category.number: category for category in FormulaRegistry.categories()}
    node_kind = "f" if isinstance(node, Formula) else "c"

    # --- act --------------------------
    matches = [_NAME_PATTERN.fullmatch(part) for part in parts]

    # --- assert -----------------------
    assert all(matches), f"catalog path {parts} has a part that is not c<NN>_<slug> or f<NN>_<slug>"
    assert [m["kind"] for m in matches] == ["c"] * (len(parts) - 1) + [node_kind]
    assert tuple(int(m["number"]) for m in matches) == node.number
    ancestor_slugs = [categories[node.number[:i]].name_slug for i in range(1, len(node.number))]
    assert [m["slug"] for m in matches] == [*ancestor_slugs, node.name_slug]


def test_catalog_holds_categories_and_formulas():
    """Assert that the catalog contains both a category and a formula.

    Without both, `test_catalog_path_matches_number_and_names` could pass vacuously.
    """
    # --- act --------------------------
    nodes = _catalog_nodes()

    # --- assert -----------------------
    assert any(isinstance(node, Formula) for node in nodes)
    assert any(not isinstance(node, Formula) for node in nodes)
