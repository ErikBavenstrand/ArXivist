from abc import ABC, abstractmethod

from arxivist.domain import model


class AbstractArXivPaperExtractor(ABC):
    """Abstract paper extractor for fetching papers from ArXiv."""

    @abstractmethod
    def fetch_recent_papers(self, categories: set[model.Category]) -> list[model.Paper]:
        """Fetches the latest papers from the ArXiv RSS feed for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Returns:
            A list of `Paper` domain objects.
        """
        raise NotImplementedError
