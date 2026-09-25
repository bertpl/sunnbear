"""The artifact registry holds the declared data artifacts and looks one up by name.

Defining a concrete `Artifact` subclass registers it here. The registry itself imports nothing: an
artifact is registered when the module that declares it is imported.
"""

from typing import TYPE_CHECKING, ClassVar

from .exceptions import ArtifactError

if TYPE_CHECKING:  # type-only: artifact imports this module at runtime, so a runtime import here would be circular
    from .artifact import Artifact


# ==================================================================================================
#  ArtifactRegistry
# ==================================================================================================
class ArtifactRegistry:
    """`ArtifactRegistry` enumerates the declared data artifacts, or looks one up by name."""

    _artifacts_by_name: ClassVar[dict[str, "type[Artifact]"]] = {}

    @classmethod
    def register(cls, artifact_cls: "type[Artifact]") -> None:
        """Register a declaration under its name.

        Raises:
            ValueError: If another declaration already has the same name.
        """
        existing = cls._artifacts_by_name.get(artifact_cls.name)
        if existing is not None:
            raise ValueError(
                f"Duplicate artifact name {artifact_cls.name!r}: {artifact_cls.__name__} and {existing.__name__}."
            )
        cls._artifacts_by_name[artifact_cls.name] = artifact_cls

    @classmethod
    def artifacts(cls) -> "tuple[type[Artifact], ...]":
        """Return every declared artifact, sorted by name."""
        return tuple(artifact_cls for _, artifact_cls in sorted(cls._artifacts_by_name.items()))

    @classmethod
    def artifact_from_name(cls, name: str) -> "type[Artifact]":
        """Return the declaration with this name.

        Raises:
            ArtifactError: If no declared artifact has this name.
        """
        artifact_cls = cls._artifacts_by_name.get(name)
        if artifact_cls is None:
            raise ArtifactError(f"No declared artifact named {name!r}.")
        return artifact_cls
