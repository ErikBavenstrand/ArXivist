import datetime

import pytest
from sqlalchemy.orm import Session

from arxivist.application.ports.persistence.repository import CategoryNotFoundError, PaperNotFoundError
from arxivist.domain.model import Category, Paper
from arxivist.infrastructure.persistence.repository import SqlAlchemyPaperRepository


@pytest.fixture
def sample_paper() -> Paper:
    return Paper(
        arxiv_id="2025.12345",
        title="Sample Paper",
        abstract="This is a sample abstract.",
        published_at=datetime.date(2025, 1, 1),
        categories=[Category("cs", "CV"), Category("cs", "CL")],
    )


class TestSqlAlchemyPaperRepository:
    def test_upsert_and_get_paper(self, in_memory_sqlite_session: Session, sample_paper: Paper) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.upsert_paper(sample_paper)
        retrieved_paper = repo.get_paper(sample_paper.arxiv_id)

        assert retrieved_paper is not None
        assert retrieved_paper.arxiv_id == sample_paper.arxiv_id
        assert retrieved_paper.title == sample_paper.title
        assert retrieved_paper.abstract == sample_paper.abstract
        assert retrieved_paper.published_at == sample_paper.published_at
        assert set(retrieved_paper.categories) == set(sample_paper.categories)

        repo.delete_paper(sample_paper.arxiv_id)
        all_papers = repo.list_papers()
        assert len(all_papers) == 0

    def test_prevent_duplicate_upsert_paper(self, in_memory_sqlite_session: Session, sample_paper: Paper) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.upsert_paper(sample_paper)
        repo.upsert_paper(sample_paper)

        all_papers = repo.list_papers()
        assert len(all_papers) == 1
        assert all_papers[0].arxiv_id == sample_paper.arxiv_id

        repo.delete_paper(sample_paper.arxiv_id)
        papers = repo.list_papers()
        assert len(papers) == 0

    def test_delete_paper(self, in_memory_sqlite_session: Session, sample_paper: Paper) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.upsert_paper(sample_paper)
        repo.delete_paper(sample_paper.arxiv_id)

        all_papers = repo.list_papers()
        assert len(all_papers) == 0

    def test_list_papers(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        sample_paper_1 = Paper(
            arxiv_id="2025.67890",
            title="Another Sample Paper",
            abstract="This is another sample abstract.",
            published_at=datetime.date(2025, 1, 2),
            categories=[Category("cs", "NLP")],
        )
        sample_paper_2 = Paper(
            arxiv_id="2025.54321",
            title="Yet Another Sample Paper",
            abstract="This is yet another sample abstract.",
            published_at=datetime.date(2025, 1, 1),
            categories=[Category("cs", "CV")],
        )

        repo.upsert_paper(sample_paper_1)
        repo.upsert_paper(sample_paper_2)

        papers = repo.list_papers()

        assert len(papers) == 2
        assert papers[0].arxiv_id == sample_paper_1.arxiv_id
        assert papers[1].arxiv_id == sample_paper_2.arxiv_id

        repo.delete_paper(sample_paper_1.arxiv_id)
        repo.delete_paper(sample_paper_2.arxiv_id)

        all_papers = repo.list_papers()
        assert len(all_papers) == 0

    def test_upsert_update_paper(self, in_memory_sqlite_session: Session, sample_paper: Paper) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        repo.upsert_paper(sample_paper)
        updated_paper = Paper(
            arxiv_id=sample_paper.arxiv_id,
            title="Updated Title",
            abstract=sample_paper.abstract,
            published_at=sample_paper.published_at,
            categories=sample_paper.categories,
        )
        repo.upsert_paper(updated_paper)

        retrieved_paper = repo.get_paper(sample_paper.arxiv_id)
        assert retrieved_paper is not None
        assert retrieved_paper.title == "Updated Title"

        repo.delete_paper(sample_paper.arxiv_id)
        all_papers = repo.list_papers()
        assert len(all_papers) == 0

    def test_delete_paper_not_found(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        with pytest.raises(PaperNotFoundError):
            repo.delete_paper("nonexistent_id")

    def test_upsert_category(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        categories = [
            Category("cs", "AI"),
            Category("cs", "ML"),
        ]
        for category in categories:
            repo.upsert_category(category)

        retrieved_categories = [repo.get_category(category.archive, category.subcategory) for category in categories]
        assert len(retrieved_categories) == len(categories)
        for retrieved_category, category in zip(retrieved_categories, categories, strict=True):
            assert isinstance(retrieved_category, Category)
            assert retrieved_category == category

        for category in categories:
            repo.delete_category(category.archive, category.subcategory)

    def test_upsert_update_category(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        category = Category("cs", "AI")
        repo.upsert_category(category)

        updated_category = Category("cs", "AI", description="Updated description")
        repo.upsert_category(updated_category)

        retrieved_category = repo.get_category(category.archive, category.subcategory)
        assert retrieved_category is not None
        assert retrieved_category.description == "Updated description"

        repo.delete_category(category.archive, category.subcategory)

    def test_delete_category(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        category = Category("cs", "AI")
        repo.upsert_category(category)
        repo.delete_category(category.archive, category.subcategory)

        retrieved_category = repo.get_category(category.archive, category.subcategory)
        assert retrieved_category is None

    def test_delete_category_not_found(self, in_memory_sqlite_session: Session) -> None:
        repo = SqlAlchemyPaperRepository(in_memory_sqlite_session)

        with pytest.raises(CategoryNotFoundError):
            repo.delete_category("Non", "existent")
