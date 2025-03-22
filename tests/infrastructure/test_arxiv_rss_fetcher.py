import datetime
import time

import pytest

from arxivist.application.ports.rss_fetcher import AbstractRSSFetcher
from arxivist.domain import model
from arxivist.domain.model import Paper
from arxivist.infrastructure.arxiv_rss_fetcher import ArXivRSSPaperExtractor
from arxivist.infrastructure.exceptions import ArXivRSSMissingFieldError


class FakeRSSFetcher(AbstractRSSFetcher):
    def __init__(self, parse_result: dict) -> None:
        self.parse_result = parse_result

    def parse(self, feed: str) -> dict:
        return self.parse_result


class TestArXivRSSPaperExtractor:
    def test_fetch_papers_success(self) -> None:
        fake_rss_fetcher = FakeRSSFetcher({
            "entries": [
                {
                    "id": "2025.12345",
                    "title": "Sample Paper",
                    "summary": "This is a sample abstract.",
                    "published_parsed": time.struct_time((2025, 1, 1, 4, 0, 0, 1, 1, 0)),
                    "tags": [{"term": "cs.CV"}, {"term": "cs.CL"}],
                },
                {
                    "id": "2025.67890",
                    "title": "Another Sample Paper",
                    "summary": "This is another sample abstract.",
                    "published_parsed": time.struct_time((2025, 1, 2, 4, 0, 0, 2, 2, 0)),
                    "tags": [{"term": "cs.NLP"}],
                },
            ],
        })
        client = ArXivRSSPaperExtractor(fake_rss_fetcher)

        papers = client.fetch_recent_papers({model.Category("cs", "CV")})

        assert len(papers) == 2
        paper_1, paper_2 = papers
        assert isinstance(paper_1, Paper)
        assert paper_1.arxiv_id == "2025.12345"
        assert paper_1.title == "Sample Paper"
        assert paper_1.abstract == "This is a sample abstract."
        assert paper_1.published_at == datetime.date(2025, 1, 1)
        assert paper_1.categories == {model.Category("cs", "CV"), model.Category("cs", "CL")}

        assert isinstance(paper_2, Paper)
        assert paper_2.arxiv_id == "2025.67890"
        assert paper_2.title == "Another Sample Paper"
        assert paper_2.abstract == "This is another sample abstract."
        assert paper_2.published_at == datetime.date(2025, 1, 2)
        assert paper_2.categories == {model.Category("cs", "NLP")}

    def test_fetch_papers_missing_fields(self) -> None:
        fake_rss_fetcher = FakeRSSFetcher({"entries": [{}]})

        client = ArXivRSSPaperExtractor(fake_rss_fetcher)

        with pytest.raises(ArXivRSSMissingFieldError, match="Missing required field 'id' in the RSS feed entry"):
            client.fetch_recent_papers({model.Category("cs", "CV")})

    def test_fetch_papers_empty_entries(self) -> None:
        fake_rss_fetcher = FakeRSSFetcher({})

        client = ArXivRSSPaperExtractor(fake_rss_fetcher)
        papers = client.fetch_recent_papers({model.Category("cs", "CV")})

        assert papers == []
