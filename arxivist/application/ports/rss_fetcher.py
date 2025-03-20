from abc import ABC, abstractmethod
from typing import Any


class AbstractRSSFetcher(ABC):
    """Abstract RSS fetcher for reading and parsing RSS feeds."""

    @staticmethod
    @abstractmethod
    def parse(feed: str) -> dict[str, Any]:
        """Parses the given RSS feed and returns a dictionary of feed data.

        Args:
            feed: The RSS feed to parse, as a url or file path.

        Returns:
            A parsed RSS feed as a dictionary.
        """
        raise NotImplementedError
