from abc import ABC, abstractmethod

from arxivist.domain.paper import Category, Paper


class AbstractArXivClient(ABC):
    """Abstract ArXiv client for fetching papers."""

    @abstractmethod
    def fetch_papers(self, categories: set[Category]) -> list[Paper]:
        """Fetches papers from ArXiv for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Returns:
            A list of `Paper` domain objects.
        """
        raise NotImplementedError
