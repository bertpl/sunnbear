"""`common_dict_keys` and `any_value_of_common_key_differs` compare 2 mappings on the keys that both hold."""

from collections.abc import Mapping


def common_dict_keys(by_key: Mapping[str, object], other_by_key: Mapping[str, object]) -> list[str]:
    """Return the sorted keys that both mappings hold."""
    return sorted(by_key.keys() & other_by_key.keys())


def any_value_of_common_key_differs(by_key: Mapping[str, object], other_by_key: Mapping[str, object]) -> bool:
    """Return whether a key that both mappings hold maps to different values in them."""
    return any(by_key[key] != other_by_key[key] for key in common_dict_keys(by_key, other_by_key))
