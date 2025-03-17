import datetime
import time

import feedparser
from feedparser import FeedParserDict

from arxivist.application.ports.arxiv_client import AbstractArXivClient
from arxivist.domain.paper import Category, Paper


class ArXivRSSClient(AbstractArXivClient):
    """An ArXiv client that fetches papers from the ArXiv RSS feed."""

    ARXIV_RSS_URL = "https://arxiv.org/rss/"
    """The ArXiv RSS feed URL."""

    def fetch_papers(self, categories: set[Category]) -> list[Paper]:
        """Fetches the latest papers from the ArXiv RSS feed for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Raises:
            ValueError: If any of the required fields are missing in the RSS feed.

        Returns:
            A list of `Paper` domain objects.
        """
        papers: list[Paper] = []
        arxiv_rss_url = f"{self.ARXIV_RSS_URL}{'+'.join(map(str, categories))}"
        entries: list[FeedParserDict] = feedparser.parse(arxiv_rss_url).get(  # type: ignore
            "entries", []
        )

        for entry in entries:
            try:
                arxiv_id = self._extract_arxiv_id(entry)
                title = self._extract_title(entry)
                abstract = self._extract_abstract(entry)
                published_at = self._extract_published_date(entry)
                paper_categories = self._extract_categories(entry)

                paper = Paper(
                    arxiv_id=arxiv_id,
                    title=title,
                    abstract=abstract,
                    published_at=published_at,
                    categories=paper_categories,
                )
                papers.append(paper)

            except ValueError as e:
                raise e

        return papers

    @staticmethod
    def _extract_arxiv_id(entry: FeedParserDict) -> str:
        """Extracts the ArXiv ID from an RSS feed entry.

        Args:
            entry: The RSS feed entry.

        Raises:
            ValueError: If the ArXiv ID is missing.

        Returns:
            The ArXiv ID.
        """
        arxiv_id: str | None = entry.get("id")  # type: ignore
        if arxiv_id is None:
            raise ValueError("Missing ArXiv ID")
        return arxiv_id.split(":")[-1].strip()

    @staticmethod
    def _extract_title(entry: FeedParserDict) -> str:
        """Extracts the title from an RSS feed entry.

        Args:
            entry: The RSS feed entry.

        Raises:
            ValueError: If the title is missing.

        Returns:
            The title.
        """
        title: str | None = entry.get("title")  # type: ignore
        if title is None:
            raise ValueError("Missing title")
        return title.strip()

    @staticmethod
    def _extract_abstract(entry: FeedParserDict) -> str:
        """Extracts the abstract from an RSS feed entry.

        Args:
            entry: The RSS feed entry.

        Raises:
            ValueError: If the abstract is missing.

        Returns:
            The abstract.
        """
        abstract: str | None = entry.get("summary")  # type: ignore
        if abstract is None:
            raise ValueError("Missing abstract")
        return abstract.split("Abstract:")[-1].strip().replace("\n", " ")

    @staticmethod
    def _extract_published_date(entry: FeedParserDict) -> datetime.date:
        """Extracts the published date from an RSS feed entry.

        Args:
            entry: The RSS feed entry.

        Raises:
            ValueError: If the published date is missing.

        Returns:
            The published date.
        """
        published_parsed: time.struct_time | None = entry.get("published_parsed")  # type: ignore
        if published_parsed is None:
            raise ValueError("Missing published date")
        return datetime.datetime.fromtimestamp(time.mktime(published_parsed)).date()

    @staticmethod
    def _extract_categories(entry: FeedParserDict) -> set[Category]:
        """Extracts the categories from an RSS feed entry.

        Args:
            entry: The RSS feed entry.

        Returns:
            A set of `Category` domain objects.
        """
        tags: list[str] = [
            tag.get("term", None)
            for tag in entry.get("tags", [])  # type: ignore
            if tag.get("term")
        ]
        return {Category.from_string(tag) for tag in tags}
