import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

from arxivist.domain import model


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


class AbstractArXivPaperExtractor(ABC):
    """Abstract paper extractor for fetching papers from ArXiv."""

    @abstractmethod
    def fetch_recent_papers(self, categories: list[model.Category]) -> list[PaperDTO]:
        """Fetches the latest papers from the ArXiv RSS feed for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Returns:
            A list of `PaperDTO` objects representing the papers.
        """
        raise NotImplementedError
