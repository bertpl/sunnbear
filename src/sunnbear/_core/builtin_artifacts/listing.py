"""This module lists the built-in data artifacts, and reads the manifest of one of them."""

import functools
import importlib
import pkgutil

from sunnbear._core.data import ArtifactDeclaration, ArtifactError, ArtifactManifest, ArtifactRegistry, ArtifactStore

# `_import_core_modules` imports every module of this package, so that every built-in declaration is registered.
_CORE_PACKAGE = "sunnbear._core"


def artifact_names() -> tuple[str, ...]:
    """Return the names of sunnbear's built-in data artifacts, sorted."""
    return tuple(declaration_cls.name for declaration_cls in _builtin_declarations())


def artifact_manifest(name: str) -> ArtifactManifest:
    """Return the manifest of the built-in data artifact with this name, without reading or downloading its data files.

    Raises:
        ArtifactError: If sunnbear has no data artifact with this name, or its manifest is missing
            or malformed.
    """
    declarations_by_name = {declaration_cls.name: declaration_cls for declaration_cls in _builtin_declarations()}
    if name not in declarations_by_name:
        raise ArtifactError(
            f"sunnbear has no data artifact named {name!r}; its data artifacts are {sorted(declarations_by_name)}."
        )
    return ArtifactStore.load_manifest(declarations_by_name[name])


def register_builtin_declarations() -> None:
    """Import every module of `sunnbear._core`, so that every built-in declaration is registered.

    The imports run once per process; later calls return immediately.
    """
    _import_core_modules()


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _builtin_declarations() -> tuple[type[ArtifactDeclaration], ...]:
    """Return the declarations that are defined inside sunnbear, sorted by name, after registering them all."""
    register_builtin_declarations()
    return ArtifactRegistry.builtin_declarations()


@functools.cache
def _import_core_modules() -> None:
    """Import every module of `sunnbear._core`, once per process."""
    core_package = importlib.import_module(_CORE_PACKAGE)
    for module_info in pkgutil.walk_packages(core_package.__path__, prefix=f"{_CORE_PACKAGE}."):
        importlib.import_module(module_info.name)
