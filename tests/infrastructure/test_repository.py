import datetime

import pytest
from sqlalchemy.orm import Session

from arxivist.domain.paper import Category, Paper
from arxivist.infrastructure.repository import SqlAlchemyPaperRepository


@pytest.fixture
def sample_paper() -> Paper:
    return Paper(
        arxiv_id="2025.12345",
        title="Sample Paper",
        abstract="This is a sample abstract.",
        published_at=datetime.date(2025, 1, 1),
        categories={Category("cs", "CV"), Category("cs", "CL")},
    )


class TestSqlAlchemyPaperRepository:
    def test_add_and_get_paper(
        self, in_memory_sqlite_session: Session, sample_paper: Paper
    ) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.add(sample_paper)
        retrieved_paper = repo.get(sample_paper.arxiv_id)

        assert retrieved_paper is not None
        assert retrieved_paper.arxiv_id == sample_paper.arxiv_id
        assert retrieved_paper.title == sample_paper.title
        assert retrieved_paper.abstract == sample_paper.abstract
        assert retrieved_paper.published_at == sample_paper.published_at
        assert retrieved_paper.categories == sample_paper.categories

        repo.delete(sample_paper.arxiv_id)
        all_papers = repo.list()
        assert len(all_papers) == 0

    def test_prevent_duplicate_add_paper(
        self, in_memory_sqlite_session: Session, sample_paper: Paper
    ) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.add(sample_paper)
        repo.add(sample_paper)

        all_papers = repo.list()
        assert len(all_papers) == 1
        assert all_papers[0].arxiv_id == sample_paper.arxiv_id

        repo.delete(sample_paper.arxiv_id)
        papers = repo.list()
        assert len(papers) == 0

    def test_delete_paper(
        self, in_memory_sqlite_session: Session, sample_paper: Paper
    ) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.add(sample_paper)
        repo.delete(sample_paper.arxiv_id)

        all_papers = repo.list()
        assert len(all_papers) == 0

    def test_list_papers(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        sample_paper_1 = Paper(
            arxiv_id="2025.67890",
            title="Another Sample Paper",
            abstract="This is another sample abstract.",
            published_at=datetime.date(2025, 1, 2),
            categories={Category("cs", "NLP")},
        )
        sample_paper_2 = Paper(
            arxiv_id="2025.54321",
            title="Yet Another Sample Paper",
            abstract="This is yet another sample abstract.",
            published_at=datetime.date(2025, 1, 1),
            categories={Category("cs", "CV")},
        )

        repo.add(sample_paper_1)
        repo.add(sample_paper_2)

        papers = repo.list()

        assert len(papers) == 2
        assert papers[0].arxiv_id == sample_paper_1.arxiv_id
        assert papers[1].arxiv_id == sample_paper_2.arxiv_id

        repo.delete(sample_paper_1.arxiv_id)
        repo.delete(sample_paper_2.arxiv_id)

        all_papers = repo.list()
        assert len(all_papers) == 0
