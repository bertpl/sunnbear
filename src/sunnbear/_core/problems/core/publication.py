"""`Publication` holds a category's publication as 1 item of CSL-JSON, the data model of the Citation Style Language."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# A citation key is a name in letters, the year's last 2 digits, and a lowercase letter where 2 keys would collide.
_CITATION_KEY_PATTERN = re.compile(r"[A-Z][A-Za-z]*(?P<year_digits>[0-9]{2})[a-z]?")


# ==================================================================================================
#  Publication
# ==================================================================================================
@dataclass(frozen=True)
class Publication:
    """`Publication` holds a publication as 1 CSL-JSON item, from which a citation processor renders its citation.

    A publication is any kind of source of formulas:

    - an article or a book;
    - a web page;
    - a code repository or a data set.

    CSL-JSON is the data model of the Citation Style Language, which Zotero and Pandoc use: an item is a JSON object
    with a ``type``, such as ``article-journal``, ``book`` or ``software``, and the fields of that type, such as
    ``container-title`` for a journal and ``publisher`` for a book's publisher.

    sunnbear renders no citation; a citation processor renders each item in a citation style of its choice.

    Every field keeps the meaning that CSL gives it:

    - ``issued`` is the date of issue: that of an article's issue, a book's edition, or a code repository's release
      or commit;
    - ``available-date`` is an earlier online date;
    - ``note`` holds a remark for a reader of the publication, such as where the authors' code is.

    A remark about 1 formula goes in the ``notes`` of that formula's presentation, and a remark for the maintainers of
    the catalog goes in the ``notes`` of the publication's source file in the survey of published test problems.

    Building a publication does not check its item against the published CSL-JSON schema; the catalog's tests check
    every shipped item against it.

    Attributes:
        csl_item: The publication as 1 CSL-JSON item, a plain dict that `json.dumps` can serialize. Its ``id`` is the
            publication's citation key: the first author's surname, or a project's name, and the year's last 2 digits,
            with a lowercase letter where 2 keys would collide, such as "Brent71" or "Ganchovski26a".
    """

    csl_item: dict[str, Any] = field(hash=False)

    def __post_init__(self) -> None:
        """Check that the item's ``id`` is a citation key whose 2 digits are the last 2 digits of the item's `year`.

        Raises:
            KeyError: If the item has no ``id``.
            ValueError: If the ``id`` is not a capitalized name, 2 digits and an optional lowercase letter, or if the
                item has a year and the ``id``'s 2 digits are not the year's last 2 digits.
        """
        citation_key = self.citation_key
        match = _CITATION_KEY_PATTERN.fullmatch(citation_key)
        if match is None:
            raise ValueError(
                f"Publication: the citation key {citation_key!r} is not a capitalized name, the year's last 2 digits, "
                "and an optional lowercase letter."
            )
        year = self.year
        if year is not None and match["year_digits"] != f"{year % 100:02d}":
            raise ValueError(
                f"Publication: the citation key {citation_key!r} does not end in the last 2 digits of the year {year}."
            )

    # --------------------------------------------------------------------------
    #  Fields of the item
    # --------------------------------------------------------------------------
    @property
    def citation_key(self) -> str:
        """Return the publication's citation key, the item's ``id``."""
        return str(self.csl_item["id"])

    @property
    def year(self) -> int | None:
        """Return the year of the item's ``issued``, or of its ``accessed`` where it has no ``issued``, or None."""
        for date_field in ("issued", "accessed"):
            date = self.csl_item.get(date_field)
            if isinstance(date, dict) and "date-parts" in date:
                return int(date["date-parts"][0][0])
        return None

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_csl_json_file(cls, path: Path) -> "Publication":
        """Return the publication of the CSL-JSON item that the file at `path` holds as 1 JSON object."""
        csl_item = json.loads(path.read_text(encoding="utf-8"))
        return cls(csl_item=csl_item)
