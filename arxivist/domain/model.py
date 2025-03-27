import datetime
from dataclasses import dataclass, field


@dataclass
class Paper:
    """Domain object for an ArXiv paper."""

    arxiv_id: str
    """The ArXiv ID of the paper."""

    title: str
    """The title of the paper."""

    abstract: str
    """The abstract of the paper."""

    published_at: datetime.date
    """The date the paper was published."""

    categories: list["Category"] = field(default_factory=list)
    """The categories the paper belongs to."""

    def __repr__(self) -> str:
        """Return the string representation of the `Paper` domain object.

        Returns:
            The string representation of the `Paper` domain object.
        """
        return (
            f"Paper(arxiv_id={self.arxiv_id!r}, title={self.title!r}, "
            f"published_at={self.published_at!r}, categories={self.categories!r}, ...)"
        )

    @property
    def published_at_int(self) -> int:
        """Return the published date as an integer.

        Returns:
            The published date as an integer in YYYYMMDD format.
        """
        return int(self.published_at.strftime("%Y%m%d"))

    @property
    def summary_url(self) -> str:
        """Return the URL to the summary of the paper.

        Returns:
            The URL to the summary of the paper.
        """
        return f"https://arxiv.org/abs/{self.arxiv_id}"

    @property
    def pdf_url(self) -> str:
        """Return the URL to the PDF of the paper.

        Returns:
            The URL to the PDF of the paper.
        """
        return f"https://arxiv.org/pdf/{self.arxiv_id}"

    @property
    def html_url(self) -> str:
        """Return the URL to the HTML version of the paper.

        Returns:
            The URL to the HTML version of the paper.
        """
        return f"https://arxiv.org/html/{self.arxiv_id}"


@dataclass(frozen=True)
class Category:
    """Domain object for an ArXiv category."""

    archive: str
    """The archive to which the category belongs (e.g., "astro-ph")."""

    subcategory: str | None
    """The subcategory of the category (e.g., "SR" for "astro-ph.SR")."""

    archive_name: str | None = None
    """The name of the category archive (e.g., "Astrophysics")."""

    category_name: str | None = None
    """The name of the category (e.g., "Solar and Stellar Astrophysics")."""

    description: str | None = None
    """The description of the category."""

    @property
    def identifier(self) -> str:
        """The identifier of the category in the format "archive.subcategory"."""
        return f"{self.archive}.{self.subcategory}" if self.subcategory else self.archive

    def __repr__(self) -> str:
        """Return the string representation of the `Category` domain object.

        Returns:
            The string representation of the `Category` domain object.
        """
        return (
            f"Category(archive={self.archive!r}, subcategory={self.subcategory!r}, "
            f"archive_name={self.archive_name!r}, category_name={self.category_name!r}, "
            f"description={self.description!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Compare the `Category` domain object with another object.

        Args:
            other: The other object to compare with.

        Returns:
            `True` if the two `Category` domain objects are equal, otherwise `False`.
        """
        if not isinstance(other, Category):
            return False

        return self.archive == other.archive and self.subcategory == other.subcategory

    def __hash__(self) -> int:
        """Hash the `Category` domain object.

        Returns:
            The hash of the `Category` domain object.
        """
        return hash((self.archive, self.subcategory))

    @staticmethod
    def from_string(category_string: str) -> "Category":
        """Create a `Category` domain object from a string.

        Args:
            category_string: The category string in the format "archive.subcategory".

        Returns:
            The `Category` domain object.
        """
        return Category(*Category.split_string(category_string))

    @staticmethod
    def split_string(category_string: str) -> tuple[str, str | None]:
        """Split a category string into archive and subcategory.

        Args:
            category_string: The category string in the format "archive.subcategory".

        Returns:
            A tuple containing the archive and subcategory.
        """
        parts = category_string.split(".")
        return parts[0], parts[1] if len(parts) > 1 else None
