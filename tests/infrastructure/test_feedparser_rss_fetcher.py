import pytest

from arxivist.infrastructure.feedparser_rss_fetcher import FeedparserRSSClient


class TestFeedparserRSSClient:
    def test_parse_valid_feed(self) -> None:
        rss_feed = "<rss><channel><title>Sample Feed</title></channel><item><title>Sample Item</title></item></rss>"
        expected_parsed_feed = {
            "bozo": False,
            "entries": [
                {
                    "title": "Sample Item",
                    "title_detail": {
                        "type": "text/plain",
                        "language": None,
                        "base": "",
                        "value": "Sample Item",
                    },
                }
            ],
            "feed": {
                "title": "Sample Feed",
                "title_detail": {
                    "type": "text/plain",
                    "language": None,
                    "base": "",
                    "value": "Sample Feed",
                },
            },
            "headers": {},
            "encoding": "utf-8",
            "version": "rss",
            "namespaces": {},
        }
        client = FeedparserRSSClient()

        result = client.parse(rss_feed)
        assert result == expected_parsed_feed

    def test_parse_invalid_feed(self) -> None:
        rss_feed = "<rss><channel><title>Sample Feed</title></channel><item><title>Sample Item</title></item>"
        client = FeedparserRSSClient()

        with pytest.raises(ValueError):
            client.parse(rss_feed)

    def test_parse_empty_feed(self) -> None:
        rss_feed = ""
        expected_parsed_feed = {"bozo": False, "entries": [], "feed": {}, "headers": {}}
        client = FeedparserRSSClient()

        result = client.parse(rss_feed)
        assert result == expected_parsed_feed
