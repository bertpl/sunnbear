import pytest

from sunnbear.functions import FormulaRegistry


@pytest.fixture
def isolated_registry(monkeypatch):
    """Give the test its own copy of the registry, so test-defined formulas and categories don't leak past the test."""
    monkeypatch.setattr(FormulaRegistry, "_formulas_by_number", dict(FormulaRegistry._formulas_by_number))
    monkeypatch.setattr(FormulaRegistry, "_categories_by_number", dict(FormulaRegistry._categories_by_number))
    monkeypatch.setattr(FormulaRegistry, "_is_taxonomy_validated", False)
