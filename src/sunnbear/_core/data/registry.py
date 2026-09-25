"""The artifact registry holds the declared data artifacts and looks one up by name.

Defining a concrete `ArtifactDeclaration` subclass registers it here. The registry does not import
any module that declares an artifact: an artifact is registered only when the module that declares
it is imported.
"""

from typing import TYPE_CHECKING, ClassVar

from .exceptions import ArtifactError

# `ArtifactDeclaration` is imported for type checking only: `declaration.py` imports this module at
# runtime, so a runtime import here would be circular.
if TYPE_CHECKING:
    from .declaration import ArtifactDeclaration


# ==================================================================================================
#  ArtifactRegistry
# ==================================================================================================
class ArtifactRegistry:
    """`ArtifactRegistry` enumerates the declared data artifacts, or looks one up by name."""

    _declarations_by_name: ClassVar[dict[str, "type[ArtifactDeclaration]"]] = {}

    @classmethod
    def register(cls, declaration_cls: "type[ArtifactDeclaration]") -> None:
        """Register a declaration under its name; defining a concrete `ArtifactDeclaration` subclass calls this.

        Raises:
            ValueError: If another declaration already has the same name.
        """
        existing_cls = cls._declarations_by_name.get(declaration_cls.name)
        if existing_cls is not None:
            raise ValueError(
                f"Duplicate artifact name {declaration_cls.name!r}: "
                f"{declaration_cls.__name__} and {existing_cls.__name__}."
            )
        cls._declarations_by_name[declaration_cls.name] = declaration_cls

    @classmethod
    def declarations(cls) -> "tuple[type[ArtifactDeclaration], ...]":
        """Return every declaration whose module has been imported, sorted by name."""
        return tuple(declaration_cls for _, declaration_cls in sorted(cls._declarations_by_name.items()))

    @classmethod
    def declaration_from_name(cls, name: str) -> "type[ArtifactDeclaration]":
        """Return the declaration with this name.

        Raises:
            ArtifactError: If no declared artifact has this name, including one whose declaring
                module has not been imported yet.
        """
        declaration_cls = cls._declarations_by_name.get(name)
        if declaration_cls is None:
            raise ArtifactError(f"No declared artifact named {name!r}.")
        return declaration_cls
