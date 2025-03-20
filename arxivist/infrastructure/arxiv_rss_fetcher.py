import datetime
import time
from typing import Any

from arxivist.application.ports.arxiv_paper_extractor import AbstractArXivPaperExtractor
from arxivist.application.ports.rss_fetcher import AbstractRSSFetcher
from arxivist.domain import model
from arxivist.infrastructure.exceptions import ArXivRSSMissingFieldError


class ArXivRSSPaperExtractor(AbstractArXivPaperExtractor):
    """An ArXiv fetcher that extracts papers from the ArXiv RSS feed."""

    def __init__(self, rss_fetcher: AbstractRSSFetcher, rss_url: str = "https://arxiv.org/rss/") -> None:
        """Initializes the `ArXivRSSClient` with the given RSS client.

        Args:
            rss_fetcher: The RSS fetcher to use for fetching the ArXiv RSS feed.
            rss_url: The base URL for the ArXiv RSS feed.
        """
        self.rss_fetcher = rss_fetcher
        self.rss_url = rss_url

    def fetch_recent_papers(self, categories: set[model.Category]) -> list[model.Paper]:
        """Fetch the latest papers from the ArXiv RSS feed for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Returns:
            A list of `Paper` domain objects.
        """
        papers: list[model.Paper] = []
        arxiv_rss_url = f"{self.rss_url}{'+'.join(map(str, categories))}"
        entries: list[dict[str, Any]] = self.rss_fetcher.parse(arxiv_rss_url).get("entries", [])

        for entry in entries:
            arxiv_id = self._extract_arxiv_id(entry)
            title = self._extract_title(entry)
            abstract = self._extract_abstract(entry)
            published_at = self._extract_published_date(entry)
            paper_categories = self._extract_categories(entry)

            paper = model.Paper(
                arxiv_id=arxiv_id,
                title=title,
                abstract=abstract,
                published_at=published_at,
                categories=paper_categories,
            )
            papers.append(paper)

        return papers

    @staticmethod
    def _extract_arxiv_id(entry: dict[str, Any]) -> str:
        """Extracts the ArXiv ID from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            ArXivRSSMissingFieldError: If the ArXiv ID is missing.

        Returns:
            The ArXiv ID.
        """
        key = "id"
        arxiv_id: str | None = entry.get(key)
        if arxiv_id is None:
            raise ArXivRSSMissingFieldError(key)
        return arxiv_id.split(":")[-1].strip()

    @staticmethod
    def _extract_title(entry: dict[str, Any]) -> str:
        """Extracts the title from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            ArXivRSSMissingFieldError: If the title is missing.

        Returns:
            The title.
        """
        key = "title"
        title: str | None = entry.get(key)
        if title is None:
            raise ArXivRSSMissingFieldError(key)
        return title.strip()

    @staticmethod
    def _extract_abstract(entry: dict[str, Any]) -> str:
        """Extracts the abstract from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            ArXivRSSMissingFieldError: If the abstract is missing.

        Returns:
            The abstract.
        """
        key = "summary"
        abstract: str | None = entry.get(key)
        if abstract is None:
            raise ArXivRSSMissingFieldError(key)
        return abstract.split("Abstract:")[-1].strip().replace("\n", " ")

    @staticmethod
    def _extract_published_date(entry: dict[str, Any]) -> datetime.date:
        """Extracts the published date from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            ArXivRSSMissingFieldError: If the published date is missing.

        Returns:
            The published date.
        """
        key = "published_parsed"
        published_parsed: time.struct_time | None = entry.get(key)
        if published_parsed is None:
            raise ArXivRSSMissingFieldError(key)
        return datetime.datetime.fromtimestamp(time.mktime(published_parsed), tz=datetime.UTC).date()

    @staticmethod
    def _extract_categories(entry: dict[str, Any]) -> set[model.Category]:
        """Extracts the categories from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Returns:
            A set of `Category` domain objects.
        """
        tags: list[str] = [tag["term"] for tag in entry.get("tags", []) if "term" in tag]
        return {model.Category.from_string(tag) for tag in tags}
