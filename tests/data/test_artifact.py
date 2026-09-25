"""Defining a valid `ArtifactDeclaration` subclass registers it; `ArtifactRegistry` looks it up by name."""

import pytest

from sunnbear._core.data import ArtifactDeclaration, ArtifactError, ArtifactRegistry


def _define_artifact(**attrs) -> type[ArtifactDeclaration]:
    """Define a concrete `ArtifactDeclaration` subclass with the given class attributes."""
    namespace = {
        "to_files": classmethod(lambda cls, value: {"value.txt": value}),
        "from_files": classmethod(lambda cls, files: files["value.txt"]),
        **attrs,
    }
    return type("_DefinedArtifact", (ArtifactDeclaration,), namespace)


# ==================================================================================================
#  Registration
# ==================================================================================================
@pytest.mark.usefixtures("isolated_artifact_registry")
def test_defining_a_concrete_artifact_registers_it():
    """A valid concrete declaration can be looked up by its name right after its definition."""
    # --- arrange / act ----------------
    artifact_cls = _define_artifact(name="defined", data_schema_version=1)

    # --- assert -----------------------
    assert ArtifactRegistry.artifact_from_name("defined") is artifact_cls
    assert artifact_cls in ArtifactRegistry.artifacts()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_an_abstract_artifact_is_not_registered():
    """A subclass that leaves the conversions abstract is a base for declarations, not one itself."""

    # --- arrange / act ----------------
    class _AbstractArtifact(ArtifactDeclaration[str]):
        """`_AbstractArtifact` keeps `to_files` and `from_files` abstract."""

        name = "abstract_one"
        data_schema_version = 1

    # --- assert -----------------------
    with pytest.raises(ArtifactError, match="No declared artifact"):
        ArtifactRegistry.artifact_from_name("abstract_one")


@pytest.mark.usefixtures("isolated_artifact_registry")
@pytest.mark.parametrize(
    "attrs, error, message",
    [
        ({"data_schema_version": 1}, TypeError, "must define name"),
        ({"name": "no_version"}, TypeError, "must define data_schema_version"),
        ({"name": "flag", "data_schema_version": True}, TypeError, "must define data_schema_version"),
        ({"name": "Upper", "data_schema_version": 1}, ValueError, "lowercase"),
        ({"name": "1st", "data_schema_version": 1}, ValueError, "lowercase"),
    ],
)
def test_a_malformed_declaration_fails_at_definition(attrs, error, message):
    """A missing or ill-typed attribute, or a name that is not a slug, fails when the class is defined."""
    # --- act / assert -----------------
    with pytest.raises(error, match=message):
        _define_artifact(**attrs)


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_two_declarations_cannot_share_a_name():
    """Registering a second declaration under an existing name fails."""
    # --- arrange ----------------------
    _define_artifact(name="shared", data_schema_version=1)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="Duplicate artifact name 'shared'"):
        _define_artifact(name="shared", data_schema_version=2)


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_artifacts_are_sorted_by_name():
    """`artifacts` returns the declarations sorted by name, whatever the order of definition."""
    # --- arrange ----------------------
    later = _define_artifact(name="zz_later", data_schema_version=1)
    earlier = _define_artifact(name="aa_earlier", data_schema_version=1)

    # --- act --------------------------
    names = [artifact_cls.name for artifact_cls in ArtifactRegistry.artifacts() if artifact_cls in (later, earlier)]

    # --- assert -----------------------
    assert names == ["aa_earlier", "zz_later"]


def test_the_sample_declaration_converts_both_ways():
    """`SampleLinesArtifact.from_files` reverses `SampleLinesArtifact.to_files`."""
    # --- arrange ----------------------
    from .sample_artifacts import SAMPLE_LINES, SampleLinesArtifact

    # --- act --------------------------
    files = SampleLinesArtifact.to_files(SAMPLE_LINES)

    # --- assert -----------------------
    assert SampleLinesArtifact.from_files(files) == SAMPLE_LINES
