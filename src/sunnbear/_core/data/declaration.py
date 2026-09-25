"""`ArtifactDeclaration` is the base class for declaring a data artifact: its name, format and conversion to files.

A declaration says how to turn a value of type ``T`` into the artifact's files and back, and which
format version those files follow. It holds no data and touches no files.

Defining a concrete subclass validates its class attributes and registers it with
`ArtifactRegistry`, so a malformed declaration fails when its module is imported.
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import ClassVar, Generic, TypeVar

from .registry import ArtifactRegistry
from .residency import ArtifactResidency

T = TypeVar("T")

# An artifact's name is also its folder name and part of `ArtifactManifest.short_identity`
# (e.g. ``uv_tuples@3f2a9c1e``), so it stays a plain slug.
_ARTIFACT_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


# ==================================================================================================
#  ArtifactDeclaration
# ==================================================================================================
class ArtifactDeclaration(ABC, Generic[T]):
    """`ArtifactDeclaration` is the base class for artifact declarations; each concrete subclass declares one artifact.

    Example::

        class UvTuplesDeclaration(ArtifactDeclaration[UvTuples]):
            name = "uv_tuples"
            data_schema_version = 1

            @classmethod
            def to_files(cls, value: UvTuples) -> dict[str, bytes]: ...

            @classmethod
            def from_files(cls, files: Mapping[str, bytes]) -> UvTuples: ...

    Class attributes:
        name: The artifact's name: lowercase letters, digits and underscores, starting with a letter.
        data_schema_version: The version of the data files' format; bump it whenever `to_files`
            changes what it writes, so that files written under a different version are refused when
            the artifact is loaded.
        residency: Where the data files live.
    """

    name: ClassVar[str]
    data_schema_version: ClassVar[int]
    residency: ClassVar[ArtifactResidency] = ArtifactResidency.EMBEDDED

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate a concrete subclass and register it with `ArtifactRegistry`; an abstract one is skipped.

        Raises:
            TypeError: If ``name`` or ``data_schema_version`` is missing or of the wrong type; a bool
                is refused as ``data_schema_version``.
            ValueError: If ``name`` is not a valid artifact name, or another declaration already has
                the same name.
        """
        super().__init_subclass__(**kwargs)
        # ABCMeta sets `__abstractmethods__` only after `__init_subclass__` returns, so read the
        # `__isabstractmethod__` flag of each method that `ArtifactDeclaration` leaves abstract.
        abstract_methods = ArtifactDeclaration.__abstractmethods__
        if any(getattr(getattr(cls, method), "__isabstractmethod__", False) for method in abstract_methods):
            return
        cls._check_class_attributes()
        ArtifactRegistry.register(cls)

    # --------------------------------------------------------------------------
    #  Conversion between a value and its files
    # --------------------------------------------------------------------------
    @classmethod
    @abstractmethod
    def to_files(cls, value: T) -> dict[str, bytes]:
        """Return the artifact's files for `value`, as a dict that maps each path to its content.

        The dict holds at least 1 file; each path is relative to the artifact's folder, uses forward
        slashes, may name a subfolder, and must not be absolute or contain a ``..`` part.
        """

    @classmethod
    @abstractmethod
    def from_files(cls, files: Mapping[str, bytes]) -> T:
        """Rebuild the value from the output of `to_files`."""

    # --------------------------------------------------------------------------
    #  Validation
    # --------------------------------------------------------------------------
    @classmethod
    def _check_class_attributes(cls) -> None:
        """Check the declaration's required class attributes."""
        for attr, attr_type in (("name", str), ("data_schema_version", int)):
            value = getattr(cls, attr, None)
            if not isinstance(value, attr_type) or isinstance(value, bool):
                raise TypeError(f"{cls.__name__} must define {attr} as {attr_type.__name__} (got {value!r}).")
        if not _ARTIFACT_NAME_PATTERN.fullmatch(cls.name):
            raise ValueError(
                f"{cls.__name__}.name {cls.name!r} must be lowercase letters, digits and underscores, "
                "starting with a letter."
            )
