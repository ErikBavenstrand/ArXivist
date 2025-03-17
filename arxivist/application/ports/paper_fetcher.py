from abc import ABC, abstractmethod

from arxivist.domain.paper import Category, Paper


class AbstractPaperFetcher(ABC):
    """Abstract paper fetcher for extracting papers from a source."""

    @abstractmethod
    def fetch_papers(self, categories: set[Category]) -> list[Paper]:
        """Fetches papers for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Returns:
            A list of `Paper` domain objects.
        """
        raise NotImplementedError
