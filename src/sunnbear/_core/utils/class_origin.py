"""This module decides whether a class is built in, i.e. defined inside the sunnbear package."""


def is_sunnbear_module(module_name: str) -> bool:
    """Return whether ``module_name`` names the sunnbear package or one of its modules."""
    return module_name == "sunnbear" or module_name.startswith("sunnbear.")
