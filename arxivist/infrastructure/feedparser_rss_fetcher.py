from typing import Any

import feedparser

from arxivist.application.ports.rss_client import AbstractRSSClient
from arxivist.infrastructure.exceptions import RSSParsingError


class FeedparserRSSClient(AbstractRSSClient):
    """An RSS client that uses the `feedparser` library to read and parse RSS feeds."""

    def parse(self, feed: str) -> dict[str, Any]:
        """Reads and parses the given RSS feed using the `feedparser` library.

        Args:
            feed: The RSS feed to parse, as a URL or file path.

        Raises:
            RSSParsingError: If the feed is invalid.

        Returns:
            A parsed RSS feed as a dictionary
        """
        result = feedparser.parse(feed)
        if result.get("bozo") == 1:
            error_msg = f"Failed to parse RSS feed {feed!r}"
            raise RSSParsingError(error_msg)

        return result
