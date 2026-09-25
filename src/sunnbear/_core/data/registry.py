"""The artifact registry holds the declared data artifacts and looks one up by name.

Defining a concrete `ArtifactDeclaration` subclass registers it here. The registry does not import
any module that declares an artifact: an artifact is registered only when the module that declares
it is imported.
"""

from typing import TYPE_CHECKING, ClassVar

from .exceptions import ArtifactError

# Imported for type checking only: `artifact.py` imports this module at runtime, so a runtime import
# here would be circular.
if TYPE_CHECKING:
    from .artifact import ArtifactDeclaration


# ==================================================================================================
#  ArtifactRegistry
# ==================================================================================================
class ArtifactRegistry:
    """`ArtifactRegistry` enumerates the declared data artifacts, or looks one up by name."""

    _artifacts_by_name: ClassVar[dict[str, "type[ArtifactDeclaration]"]] = {}

    @classmethod
    def register(cls, artifact_cls: "type[ArtifactDeclaration]") -> None:
        """Register a declaration under its name; defining a concrete `ArtifactDeclaration` subclass calls this.

        Raises:
            ValueError: If another declaration already has the same name.
        """
        existing_cls = cls._artifacts_by_name.get(artifact_cls.name)
        if existing_cls is not None:
            raise ValueError(
                f"Duplicate artifact name {artifact_cls.name!r}: {artifact_cls.__name__} and {existing_cls.__name__}."
            )
        cls._artifacts_by_name[artifact_cls.name] = artifact_cls

    @classmethod
    def artifacts(cls) -> "tuple[type[ArtifactDeclaration], ...]":
        """Return every artifact whose declaring module has been imported, sorted by name."""
        return tuple(artifact_cls for _, artifact_cls in sorted(cls._artifacts_by_name.items()))

    @classmethod
    def artifact_from_name(cls, name: str) -> "type[ArtifactDeclaration]":
        """Return the declaration with this name.

        Raises:
            ArtifactError: If no declared artifact has this name, including one whose declaring
                module has not been imported yet.
        """
        artifact_cls = cls._artifacts_by_name.get(name)
        if artifact_cls is None:
            raise ArtifactError(f"No declared artifact named {name!r}.")
        return artifact_cls
