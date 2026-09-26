"""Defining a valid `ArtifactDeclaration` subclass registers it; `ArtifactRegistry` looks it up by name."""

import pytest

from sunnbear._core.data import ArtifactDeclaration, ArtifactError, ArtifactRegistry

from .sample_declarations import define_declaration


# ==================================================================================================
#  Registration
# ==================================================================================================
@pytest.mark.usefixtures("isolated_artifact_registry")
def test_defining_a_concrete_declaration_registers_it():
    """A valid concrete declaration can be looked up by its name right after its definition."""
    # --- arrange / act ----------------
    declaration_cls = define_declaration(name="defined")

    # --- assert -----------------------
    assert ArtifactRegistry.declaration_from_name("defined") is declaration_cls
    assert declaration_cls in ArtifactRegistry.declarations()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_an_abstract_declaration_is_not_registered():
    """A subclass that leaves `to_files` and `from_files` abstract is not registered."""

    # --- arrange / act ----------------
    class _AbstractDeclaration(ArtifactDeclaration[str]):
        """`_AbstractDeclaration` keeps `to_files` and `from_files` abstract."""

        name = "abstract_one"

    # --- assert -----------------------
    with pytest.raises(ArtifactError, match="No declared artifact"):
        ArtifactRegistry.declaration_from_name("abstract_one")


@pytest.mark.usefixtures("isolated_artifact_registry")
@pytest.mark.parametrize(
    "attrs, error, message",
    [
        ({}, TypeError, "must define name"),
        ({"name": 1}, TypeError, "must define name"),
        ({"name": "Upper"}, ValueError, "lowercase"),
        ({"name": "1st"}, ValueError, "lowercase"),
    ],
)
def test_a_malformed_declaration_fails_at_definition(attrs, error, message):
    """A missing or ill-typed name, or a name that is not a slug, fails when the class is defined."""
    # --- act / assert -----------------
    with pytest.raises(error, match=message):
        define_declaration(**attrs)


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_two_declarations_cannot_share_a_name():
    """Registering a second declaration under an existing name fails."""
    # --- arrange ----------------------
    define_declaration(name="shared")

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="Duplicate artifact name 'shared'"):
        define_declaration(name="shared")


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_declarations_are_sorted_by_name():
    """`artifacts` returns the declarations sorted by name, whatever the order of definition."""
    # --- arrange ----------------------
    later = define_declaration(name="zz_later")
    earlier = define_declaration(name="aa_earlier")

    # --- act --------------------------
    names = [
        declaration_cls.name
        for declaration_cls in ArtifactRegistry.declarations()
        if declaration_cls in (later, earlier)
    ]

    # --- assert -----------------------
    assert names == ["aa_earlier", "zz_later"]


def test_the_sample_declaration_converts_both_ways():
    """`SampleLinesDeclaration.from_files` reverses `SampleLinesDeclaration.to_files`."""
    # --- arrange ----------------------
    from .sample_declarations import SAMPLE_LINES, SampleLinesDeclaration

    # --- act --------------------------
    files = SampleLinesDeclaration.to_files(SAMPLE_LINES)

    # --- assert -----------------------
    assert SampleLinesDeclaration.from_files(files) == SAMPLE_LINES
