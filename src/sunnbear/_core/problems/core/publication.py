"""`Publication` holds the parts of a publication that the formulas of a category come from."""

import re
from dataclasses import dataclass

# A citation key is a name in letters, the year's last 2 digits, and a lowercase letter where 2 keys would collide.
_CITATION_KEY_PATTERN = re.compile(r"[A-Z][A-Za-z]*[0-9]{2}[a-z]?")


# ==================================================================================================
#  Publication
# ==================================================================================================
@dataclass(frozen=True)
class Publication:
    """`Publication` holds a publication's citation as written, and its parts: authors, year, title, DOI and more.

    A publication is any kind of source of formulas: an article, a book, a web page, a code repository or a data set.
    A `FormulaCategory` that holds exactly the formulas of 1 publication declares it.

    Every field but `citation` is None, or empty, by default; the catalog's tests require each field that a shipped
    publication has.

    Attributes:
        citation: The full citation, as a reader would cite the publication, with its DOI or URL where it has one.
        citation_key: A short name of the publication, unique among the shipped publications: the first author's
            surname, or a project's name, and the year's last 2 digits, with a lowercase letter where 2 keys would
            collide, such as "Brent71" or "Ganchovski26a".
        authors: The authors, each as the citation writes them, such as ``("Dowell, M.", "Jarratt, P.")``.
        year: The year of the publication, as the citation gives it.
        title: The title of the article, book, web page or project.
        published_in: Where the publication appeared: an article's journal, a chapter's book, a book's publisher, or
            the website or platform of a web page or code repository, such as "BIT" or "Prentice-Hall".
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
        """Check that the citation holds every part that the publication declares, and the form of the citation key.

        Raises:
            ValueError: If the citation does not hold a declared author, the year, the title, where the publication
                appeared, the DOI or the URL; or if the citation key is not a name, 2 digits and an optional letter.
        """
        if self.citation_key is not None and not _CITATION_KEY_PATTERN.fullmatch(self.citation_key):
            raise ValueError(
                f"Publication: the citation key {self.citation_key!r} is not a capitalized name, the year's last 2 "
                "digits, and an optional lowercase letter."
            )
        year = str(self.year) if self.year is not None else None
        parts = [*self.authors, year, self.title, self.published_in, self.doi, self.url]
        missing = [part for part in parts if part is not None and part not in self.citation]
        if missing:
            raise ValueError(f"Publication: the citation {self.citation!r} does not hold {missing}.")
