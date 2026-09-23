import pytest

from sunnbear._core.utils.slugify import slugify


@pytest.mark.parametrize(
    "name, slug",
    [
        ("cubic", "cubic"),
        ("Odd power", "odd_power"),
        ("User-defined", "user_defined"),
        ("  Riemann ζ (Müller)  ", "riemann_muller"),
    ],
)
def test_slugify(name, slug):
    """Slugify lowercases, drops accents and other non-ASCII characters, and joins the words with underscores."""
    assert slugify(name) == slug
