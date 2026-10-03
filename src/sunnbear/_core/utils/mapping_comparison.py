"""`common_keys_and_whether_any_differ` compares 2 mappings on the keys that both hold."""

from collections.abc import Mapping


def common_keys_and_whether_any_differ(
    by_key: Mapping[str, object], other_by_key: Mapping[str, object]
) -> tuple[list[str], bool]:
    """Return the sorted keys in both mappings, and whether any of those keys maps to different values."""
    common_keys = sorted(by_key.keys() & other_by_key.keys())
    return common_keys, any(by_key[key] != other_by_key[key] for key in common_keys)
