"""`Publication` holds the citation and the parts of the publication of a category's formulas."""

import re
from dataclasses import dataclass

# A citation key is a name in letters, the year's last 2 digits, and a lowercase letter where 2 keys would collide.
_CITATION_KEY_PATTERN = re.compile(r"[A-Z][A-Za-z]*(?P<year_digits>[0-9]{2})[a-z]?")


# ==================================================================================================
#  Publication
# ==================================================================================================
@dataclass(frozen=True)
class Publication:
    """`Publication` holds a publication's citation as written, and its parts: authors, year, title, DOI and more.

    A publication is any kind of source of formulas:

    - an article or a book;
    - a web page;
    - a code repository or a data set.

    Each part that a publication declares, except its year, appears in its citation as written, and building the
    publication checks this. The catalog's tests require a shipped publication to declare its citation key, year and
    title, and its DOI or URL where its citation holds a link.

    Attributes:
        citation: The full citation, as a reader would cite the publication, with its DOI or URL where it has one.
        citation_key: A short name of the publication, unique among the shipped publications: the first author's
            surname, or a project's name, and the year's last 2 digits, with a lowercase letter where 2 keys would
            collide, such as "Brent71" or "Ganchovski26a".
        authors: The authors, each as the citation writes them, such as ``("Dowell, M.", "Jarratt, P.")``.
        year: The year by which the catalog dates the publication. The citation may print another year, such as the
            year of an issue that came out after the article appeared online, or none, as for a code repository.
        title: The title of the article, book, web page or project.
        published_in: Where the publication appeared: an article's journal, a chapter's book, a book's publisher, or
            the website of a web page, such as "BIT" or "Prentice-Hall".
        doi: The DOI, without its ``https://doi.org/`` prefix, such as "10.1093/comjnl/14.4.422".
        url: A URL of the publication itself, for a publication without a DOI.
    """

    citation: str
    citation_key: str | None = None
    authors: tuple[str, ...] = ()
    year: int | None = None
    title: str | None = None
    published_in: str | None = None
    doi: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        """Check that the citation holds every declared part but the year, and that the citation key fits the year.

        Raises:
            ValueError: If the citation does not hold a declared author, the title, where the publication appeared,
                the DOI or the URL; if the citation key is not a name, 2 digits and an optional letter; or if its 2
                digits are not the last 2 digits of the year.
        """
        if self.citation_key is not None:
            match = _CITATION_KEY_PATTERN.fullmatch(self.citation_key)
            if match is None:
                raise ValueError(
                    f"Publication: the citation key {self.citation_key!r} is not a capitalized name, the year's last "
                    "2 digits, and an optional lowercase letter."
                )
            if self.year is not None and match["year_digits"] != f"{self.year % 100:02d}":
                raise ValueError(
                    f"Publication: the citation key {self.citation_key!r} does not end in the last 2 digits of the "
                    f"year {self.year}."
                )
        parts = [*self.authors, self.title, self.published_in, self.doi, self.url]
        missing = [part for part in parts if part is not None and part not in self.citation]
        if missing:
            raise ValueError(f"Publication: the citation {self.citation!r} does not hold {missing}.")
