"""This module decides whether a class is built in, i.e. defined inside the sunnbear package."""


def is_defined_in_sunnbear(cls: type) -> bool:
    """Return whether ``cls`` is defined in a module of the sunnbear package."""
    return cls.__module__ == "sunnbear" or cls.__module__.startswith("sunnbear.")
