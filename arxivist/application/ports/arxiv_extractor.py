import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

from arxivist.domain import model


class CategoryFetchError(Exception):
    """Raised when fetching the categories fails."""


class CategoryParseError(Exception):
    """Raised when parsing the categories fails."""


class PaperMissingFieldError(Exception):
    """Raised when a required field is missing in the paper."""

    def __init__(self, field_name: str) -> None:
        """Initializes the `PaperMissingFieldError` exception.

        Args:
            field_name: The name of the missing field.
        """
        super().__init__(f"Missing required field {field_name!r} in the paper.")


@dataclass(frozen=True)
class PaperDTO:
    """Data Transfer Object for an ArXiv paper."""

    arxiv_id: str
    """The ArXiv ID of the paper."""

    title: str
    """The title of the paper."""

    abstract: str
    """The abstract of the paper."""

    published_at: datetime.date
    """The date the paper was published."""

    categories: list[str]
    """The categories the paper belongs to."""

    def __eq__(self, other: object) -> bool:
        """Checks if two `PaperDTO` objects are equal.

        Args:
            other: The other object to compare with.

        Returns:
            True if the objects are equal, False otherwise.
        """
        if not isinstance(other, PaperDTO):
            return False

        return (
            self.arxiv_id == other.arxiv_id
            and self.title == other.title
            and self.abstract == other.abstract
            and self.published_at == other.published_at
            and self.categories == other.categories
        )

    def __hash__(self) -> int:
        """Generates a hash for the `PaperDTO` object.

        Returns:
            The hash value of the object.
        """
        return hash((self.arxiv_id, self.title, self.abstract, self.published_at, tuple(self.categories)))


@dataclass(frozen=True)
class CategoryDTO:
    """Data Transfer Object for an ArXiv category."""

    archive: str
    """The archive to which the category belongs."""

    subcategory: str | None
    """The subcategory of the category."""

    archive_name: str | None
    """The name of the category archive."""

    category_name: str | None
    """The name of the category."""

    description: str | None
    """The description of the category."""

    def __eq__(self, other: object) -> bool:
        """Checks if two `CategoryDTO` objects are equal.

        Args:
            other: The other object to compare with.

        Returns:
            True if the objects are equal, False otherwise.
        """
        if not isinstance(other, CategoryDTO):
            return False

        return (
            self.archive == other.archive
            and self.subcategory == other.subcategory
            and self.archive_name == other.archive_name
            and self.category_name == other.category_name
            and self.description == other.description
        )

    def __hash__(self) -> int:
        """Generates a hash for the `CategoryDTO` object.

        Returns:
            The hash value of the object.
        """
        return hash((self.archive, self.subcategory, self.archive_name, self.category_name, self.description))


class AbstractArXivPaperExtractor(ABC):
    """Abstract paper extractor for fetching papers from ArXiv."""

    @abstractmethod
    def fetch_latest_papers(self, categories: list[model.Category]) -> list[PaperDTO]:
        """Fetches the latest papers from the ArXiv RSS feed for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Raises:
            PaperMissingFieldError: If a required field is missing in the paper.

        Returns:
            A list of `PaperDTO` objects representing the papers.
        """
        raise NotImplementedError


class AbstractArXivCategoryExtractor(ABC):
    """Abstract category extractor for fetching categories from ArXiv."""

    @abstractmethod
    def fetch_categories(self) -> list[CategoryDTO]:
        """Fetches all categories from ArXiv.

        Raises:
            CategoryFetchError: If fetching categories fails.
            CategoryParseError: If parsing categories fails.

        Returns:
            A list of `CategoryDTO` objects representing the categories.
        """
        raise NotImplementedError
