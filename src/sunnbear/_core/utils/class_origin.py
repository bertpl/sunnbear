"""This module decides whether a class is built in, i.e. defined inside the sunnbear package."""


def is_defined_in_sunnbear(cls: type) -> bool:
    """Return whether ``cls`` is defined in a module of the sunnbear package."""
    return is_sunnbear_module(cls.__module__)


def is_sunnbear_module(module_name: str) -> bool:
    """Return whether ``module_name`` names the sunnbear package or one of its modules."""
    return module_name == "sunnbear" or module_name.startswith("sunnbear.")
