import datetime
import time
from unittest.mock import MagicMock

import pytest

from arxivist.application.ports.rss_fetcher import AbstractRSSFetcher
from arxivist.domain import Category
from arxivist.domain.paper import Paper
from arxivist.infrastructure.arxiv_rss_fetcher import ArXivRSSFetcher


class TestArXivRSSClient:
    def test_fetch_papers_success(self) -> None:
        mock_rss_fetcher = MagicMock(AbstractRSSFetcher)
        mock_rss_fetcher.parse.return_value = {
            "entries": [
                {
                    "id": "2025.12345",
                    "title": "Sample Paper",
                    "summary": "This is a sample abstract.",
                    "published_parsed": time.struct_time(
                        (2025, 1, 1, 0, 0, 0, 0, 1, 0)
                    ),
                    "tags": [{"term": "cs.CV"}, {"term": "cs.CL"}],
                },
                {
                    "id": "2025.67890",
                    "title": "Another Sample Paper",
                    "summary": "This is another sample abstract.",
                    "published_parsed": time.struct_time(
                        (2025, 1, 2, 0, 0, 0, 0, 2, 0)
                    ),
                    "tags": [{"term": "cs.NLP"}],
                },
            ]
        }

        client = ArXivRSSFetcher(mock_rss_fetcher)

        papers = client.fetch_papers({Category("cs", "CV")})

        assert len(papers) == 2
        paper_1, paper_2 = papers
        assert isinstance(paper_1, Paper)
        assert paper_1.arxiv_id == "2025.12345"
        assert paper_1.title == "Sample Paper"
        assert paper_1.abstract == "This is a sample abstract."
        assert paper_1.published_at == datetime.date(2025, 1, 1)
        assert paper_1.categories == {Category("cs", "CV"), Category("cs", "CL")}

        assert isinstance(paper_2, Paper)
        assert paper_2.arxiv_id == "2025.67890"
        assert paper_2.title == "Another Sample Paper"
        assert paper_2.abstract == "This is another sample abstract."
        assert paper_2.published_at == datetime.date(2025, 1, 2)
        assert paper_2.categories == {Category("cs", "NLP")}

    def test_fetch_papers_missing_fields(self) -> None:
        mock_rss_fetcher = MagicMock(AbstractRSSFetcher)
        mock_rss_fetcher.parse.return_value = {"entries": [{}]}

        client = ArXivRSSFetcher(mock_rss_fetcher)

        mock_rss_fetcher.parse = lambda feed: {"entries": [{}]}
        with pytest.raises(ValueError):
            client.fetch_papers({Category("cs", "CV")})
