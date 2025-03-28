import datetime
import re
import time
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup, Tag

from arxivist.application.ports.arxiv_extractor import (
    AbstractArXivCategoryExtractor,
    AbstractArXivPaperExtractor,
    CategoryDTO,
    CategoryFetchError,
    CategoryParseError,
    PaperDTO,
    PaperMissingFieldError,
)
from arxivist.domain import model


class ArXivRSSPaperExtractor(AbstractArXivPaperExtractor):
    """An ArXiv fetcher that extracts papers from the ArXiv RSS feed."""

    def __init__(self, rss_url: str = "https://arxiv.org/rss/") -> None:
        """Initializes the `ArXivRSSClient` with the given RSS client.

        Args:
            rss_url: The base URL for the ArXiv RSS feed.
        """
        self.rss_url = rss_url

    def fetch_latest_papers(self, categories: list[model.Category]) -> list[PaperDTO]:
        """Fetch the latest papers from the ArXiv RSS feed for the given categories.

        Args:
            categories: The `Category` domain objects to filter the papers by.

        Raises:
            PaperMissingFieldError: If a required field is missing in the paper.

        Returns:
            A list of `PaperDTO` objects representing the papers.
        """
        papers: list[PaperDTO] = []
        arxiv_rss_url = f"{self.rss_url}{'+'.join(category.identifier for category in categories)}"
        entries: list[dict[str, Any]] = feedparser.parse(arxiv_rss_url).get("entries", [])  # type: ignore[no-untyped-call]

        for entry in entries:
            arxiv_id = self._extract_arxiv_id(entry)
            title = self._extract_title(entry)
            abstract = self._extract_abstract(entry)
            published_at = self._extract_published_date(entry)
            paper_categories = self._extract_categories(entry)

            papers.append(
                PaperDTO(
                    arxiv_id=arxiv_id,
                    title=title,
                    abstract=abstract,
                    published_at=published_at,
                    categories=paper_categories,
                ),
            )

        return papers

    @staticmethod
    def _extract_arxiv_id(entry: dict[str, Any]) -> str:
        """Extracts the ArXiv ID from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            PaperMissingFieldError: If the ArXiv ID is missing.

        Returns:
            The ArXiv ID.
        """
        key = "id"
        arxiv_id: str | None = entry.get(key)
        if arxiv_id is None:
            raise PaperMissingFieldError(key)
        return arxiv_id.split(":")[-1].strip()

    @staticmethod
    def _extract_title(entry: dict[str, Any]) -> str:
        """Extracts the title from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            PaperMissingFieldError: If the title is missing.

        Returns:
            The title.
        """
        key = "title"
        title: str | None = entry.get(key)
        if title is None:
            raise PaperMissingFieldError(key)
        return title.strip()

    @staticmethod
    def _extract_abstract(entry: dict[str, Any]) -> str:
        """Extracts the abstract from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            PaperMissingFieldError: If the abstract is missing.

        Returns:
            The abstract.
        """
        key = "summary"
        abstract: str | None = entry.get(key)
        if abstract is None:
            raise PaperMissingFieldError(key)
        return abstract.split("Abstract:")[-1].strip().replace("\n", " ")

    @staticmethod
    def _extract_published_date(entry: dict[str, Any]) -> datetime.date:
        """Extracts the published date from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Raises:
            PaperMissingFieldError: If the published date is missing.

        Returns:
            The published date.
        """
        key = "published_parsed"
        published_parsed: time.struct_time | None = entry.get(key)
        if published_parsed is None:
            raise PaperMissingFieldError(key)
        return datetime.datetime.fromtimestamp(time.mktime(published_parsed), tz=datetime.UTC).date()

    @staticmethod
    def _extract_categories(entry: dict[str, Any]) -> list[str]:
        """Extracts the categories from an RSS feed entry.

        Args:
            entry: The RSS feed entry as a dictionary.

        Returns:
            A set of `Category` domain objects.
        """
        return [tag["term"] for tag in entry.get("tags", []) if "term" in tag]


class ArXivCategoryExtractor(AbstractArXivCategoryExtractor):
    """An ArXiv category extractor that fetches categories from the ArXiv website."""

    CATEGORY_PATTERN = re.compile(r"([a-zA-Z\-]+)(?:\.([a-zA-Z\-]+))?\s*\(([^)]+)\)")
    ARCHIVE_PATTERN = re.compile(r"^(.*?)\s*\(")

    def __init__(self, url: str = "https://arxiv.org/category_taxonomy") -> None:
        """Initializes the `ArXivCategoryExtractor` with the given URL.

        Args:
            url: The URL for the ArXiv category taxonomy page.
        """
        self.url = url

    def fetch_categories(self) -> list[CategoryDTO]:
        """Fetches all categories from ArXiv.

        Raises:
            CategoryFetchError: If fetching categories fails.
            CategoryParseError: If parsing categories fails.

        Returns:
            A list of `CategoryDTO` objects representing the categories.
        """
        soup = self._fetch_and_parse_html()
        return self._extract_categories(soup)

    def _fetch_and_parse_html(self) -> Tag:
        """Fetches the HTML content from the ArXiv category taxonomy page and parses it.

        Raises:
            CategoryFetchError: If there is an error fetching the categories.
            CategoryParseError: If there is an error parsing the categories.

        Returns:
            A BeautifulSoup Tag object representing the category taxonomy list.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            msg = f"Failed to fetch the categories from {self.url}: {e}"
            raise CategoryFetchError(msg) from e

        soup = BeautifulSoup(response.text, "html.parser").find("div", id="category_taxonomy_list")
        if not isinstance(soup, Tag):
            msg = "Failed to find the category taxonomy list in the HTML response."
            raise CategoryParseError(msg)
        return soup

    def _extract_categories(self, soup: Tag) -> list[CategoryDTO]:
        """Extracts categories from the BeautifulSoup object.

        Args:
            soup: The BeautifulSoup object representing the category taxonomy list.

        Raises:
            CategoryParseError: If there is an error parsing the categories.

        Returns:
            A list of `CategoryDTO` objects representing the categories.
        """
        categories: list[CategoryDTO] = []
        group_name: str | None = None
        archive_name: str | None = None
        archive: str | None = None
        subcategory: str | None = None
        category_name: str | None = None

        for element in soup.find_all(["h2", "h3", "h4", "p"]):
            if not isinstance(element, Tag):
                continue

            match element.name:
                case "h2":
                    group_name, archive_name, archive, subcategory, category_name = self._parse_group_header(element)
                case "h3":
                    archive_name, archive, subcategory, category_name = self._parse_archive_header(element)
                case "h4":
                    archive, subcategory, category_name = self._parse_category_header(element)
                case "p":
                    if archive is None:
                        msg = f"Missing archive for category {category_name!r} in group {group_name!r}"
                        raise CategoryParseError(msg)

                    categories.append(
                        self._create_category_dto(
                            element,
                            archive,
                            subcategory,
                            archive_name or group_name,
                            category_name,
                        ),
                    )

        return categories

    def _parse_group_header(self, element: Tag) -> tuple[str, None, None, None, None]:
        """Parses the group header element.

        Args:
            element: The HTML element representing the group header.

        Returns:
            A tuple containing the group name and None values for other fields.
        """
        return str(element.text).strip(), None, None, None, None

    def _parse_archive_header(self, element: Tag) -> tuple[str | None, None, None, None]:
        """Parses the archive header element.

        Args:
            element: The HTML element representing the archive header.
            group_name: The name of the group to which the archive belongs.

        Returns:
            _description_
        """
        archive_name = self._extract_archive_name(element.text)
        return archive_name, None, None, None

    def _parse_category_header(self, element: Tag) -> tuple[str, str | None, str]:
        """Parses the category header element.

        Args:
            element: The HTML element representing the category header.

        Raises:
            CategoryParseError: If the category header format is invalid.

        Returns:
            A tuple containing the archive, subcategory, and category name.
        """
        category_data = self._extract_category_data(element.text)
        if category_data is None:
            msg = f"Failed to parse category header {element.text!r}"
            raise CategoryParseError(msg)

        return category_data

    def _create_category_dto(
        self,
        element: Tag,
        archive: str,
        subcategory: str | None,
        archive_name: str | None,
        category_name: str | None,
    ) -> CategoryDTO:
        """Creates a `CategoryDTO` object from the given parameters.

        Args:
            element: The HTML element representing the category description.
            archive: The archive to which the category belongs.
            subcategory: The subcategory of the category.
            archive_name: The name of the category archive.
            category_name: The name of the category.

        Returns:
            A `CategoryDTO` object representing the category.
        """
        return CategoryDTO(
            archive=archive,
            subcategory=subcategory,
            archive_name=archive_name,
            category_name=category_name,
            description=str(element.text).strip(),
        )

    def _extract_category_data(self, text: str | None) -> tuple[str, str | None, str] | None:
        """Extracts the category data from the given text.

        Looks for a pattern like "archive.subcategory (category name)".

        Args:
            text: The text to extract the category data from.

        Returns:
            A tuple containing the archive, subcategory, and category name, or None if not found.
        """
        if not text:
            return None

        match = self.CATEGORY_PATTERN.match(text)
        if match:
            before_period, after_period, inside_parentheses = match.groups()
            return before_period, after_period or None, inside_parentheses
        return None

    def _extract_archive_name(self, text: str | None) -> str | None:
        """Extracts the archive name from the given text.

        Looks for a pattern like "archive (description)".

        Args:
            text: The text to extract the archive name from.

        Returns:
            The extracted archive name, or None if not found.
        """
        if not text:
            return None

        match = self.ARCHIVE_PATTERN.match(text)
        return match.group(1).strip() if match else None
