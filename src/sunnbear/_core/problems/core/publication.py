"""`Publication` holds the citation of a category's publication, and its parts: authors, year, title, DOI and more."""

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

    Each part that a publication declares appears in its citation as written, and building the publication checks this.
    The catalog's tests require a shipped publication to declare its citation key, year and title, and its DOI or URL
    where its citation holds a link.

    Attributes:
        citation: The full citation, as a reader would cite the publication, with its DOI or URL where it has one, in
            1 paragraph and without notes about the source.
        citation_key: A short name of the publication, unique among the shipped publications: the first author's
            surname, or a project's name, and the year's last 2 digits, with a lowercase letter where 2 keys would
            collide, such as "Brent71" or "Ganchovski26a".
        authors: The authors, each as the citation writes them, such as ``("Dowell, M.", "Jarratt, P.")``.
        year: The year of the publication as its citation gives it: an article's year is that of its issue, even
            where it appeared online earlier, and a code repository's is that of the cited release or commit.
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
        """Check that the citation holds every declared part, and that the citation key fits the year.

        Raises:
            ValueError: If any of these holds:
                - the citation does not hold a declared author, the year, the title, where the publication appeared,
                  the DOI or the URL;
                - the citation key is not a name, 2 digits and an optional letter;
                - the citation key's 2 digits are not the last 2 digits of the year.
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
        year = str(self.year) if self.year is not None else None
        parts = [*self.authors, year, self.title, self.published_in, self.doi, self.url]
        missing = [part for part in parts if part is not None and part not in self.citation]
        if missing:
            raise ValueError(f"Publication: the citation {self.citation!r} does not hold {missing}.")
