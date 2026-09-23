"""This package decides whether a class is built in, i.e. defined inside the sunnbear package.

Some registrations are reserved for built-in classes: a built-in-only solver role, and a formula or
category under a built-in-only top-level category.
"""


def is_defined_in_sunnbear(cls: type) -> bool:
    """Return whether ``cls`` is defined in a module of the sunnbear package."""
    return cls.__module__ == "sunnbear" or cls.__module__.startswith("sunnbear.")
