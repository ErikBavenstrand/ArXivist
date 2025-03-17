import datetime
from dataclasses import dataclass
from typing import Any


class Paper:
    """Domain object for an ArXiv paper."""

    BASE_URL = "https://arxiv.org"

    def __init__(
        self,
        arxiv_id: str,
        title: str,
        abstract: str,
        published_at: datetime.date,
        categories: set["Category"] | None = None,
    ) -> None:
        """Initializes the `Paper` domain object.

        Args:
            arxiv_id: The ArXiv ID of the paper.
            title: The title of the paper.
            abstract: The abstract of the paper.
            published_at: The date the paper was published.
            categories: The categories the paper belongs to.
        """
        self.arxiv_id: str = arxiv_id
        self.title: str = title
        self.abstract: str = abstract
        self.published_at: datetime.date = published_at
        self.categories: set[Category] = categories or set()

    def __repr__(self) -> str:
        """Return the string representation of the `Paper` domain object.

        Returns:
            The string representation of the `Paper` domain object.
        """
        return f"Paper(arxiv_id={self.arxiv_id!r}, title={self.title!r}, published_at={self.published_at!r}, ...)"

    @property
    def summary_url(self) -> str:
        """Return the URL to the summary of the paper.

        Returns:
            The URL to the summary of the paper.
        """
        return f"{self.BASE_URL}/abs/{self.arxiv_id}"

    @property
    def pdf_url(self) -> str:
        """Return the URL to the PDF of the paper.

        Returns:
            The URL to the PDF of the paper.
        """
        return f"{self.BASE_URL}/pdf/{self.arxiv_id}"

    @property
    def html_url(self) -> str:
        """Return the URL to the HTML version of the paper.

        Returns:
            The URL to the HTML version of the paper.
        """
        return f"{self.BASE_URL}/html/{self.arxiv_id}"


@dataclass(frozen=True)
class Category:
    """Domain object for an ArXiv category."""

    major: str
    """The major category (e.g., "cs")."""

    minor: str | None = None
    """The minor category (e.g., "CV")."""

    @staticmethod
    def from_string(category: str) -> "Category":
        """Create a `Category` domain object from a string.

        Args:
            category: The string representation of the category.

        Returns:
            The `Category` domain object.
        """
        return Category(*category.split(".")[:2])

    def __eq__(self, other: Any) -> bool:
        """Compare the `Category` domain object with another object.

        Args:
            other: The other object to compare with.

        Returns:
            `True` if the two `Category` domain objects are equal, otherwise `False`.
        """
        if not isinstance(other, Category):
            return False
        return self.major == other.major and self.minor == other.minor

    def __hash__(self) -> int:
        """Hash the `Category` domain object.

        Returns:
            The hash of the `Category` domain object.
        """
        return hash((self.major, self.minor))

    def __str__(self) -> str:
        """Return the string representation of the `Category` domain object.

        Returns:
            The string representation of the `Category` domain
        """
        return f"{self.major}.{self.minor}" if self.minor else self.major

    def __repr__(self) -> str:
        """Return the string representation of the `Category` domain object.

        Returns:
            The string representation of the `Category` domain
        """
        return f"Category(major={self.major!r}, minor={self.minor!r})"
