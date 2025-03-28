import datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from arxivist.domain.model import Category, Paper
from arxivist.infrastructure.persistence.repository import SqlAlchemyPaperRepository
from arxivist.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def sample_paper() -> Paper:
    return Paper(
        arxiv_id="2025.12345",
        title="Sample Paper",
        abstract="This is a sample abstract.",
        published_at=datetime.date(2025, 1, 1),
        categories=[Category("cs", "CV"), Category("cs", "CL")],
    )


class TestSqlAlchemyUnitOfWork:
    def test_commit(
        self,
        in_memory_sqlite_session_factory: sessionmaker[Session],
        sample_paper: Paper,
    ) -> None:
        uow = SqlAlchemyUnitOfWork(in_memory_sqlite_session_factory)
        with uow:
            uow.papers.upsert_paper(sample_paper)
            uow.commit()

        with uow:
            retrieved_paper = uow.papers.get_paper(sample_paper.arxiv_id)
            assert retrieved_paper is not None
            assert retrieved_paper.arxiv_id == sample_paper.arxiv_id
            assert retrieved_paper.title == sample_paper.title
            assert retrieved_paper.abstract == sample_paper.abstract
            assert retrieved_paper.published_at == sample_paper.published_at
            assert set(retrieved_paper.categories) == set(sample_paper.categories)

        with uow:
            uow.papers.delete_paper(sample_paper.arxiv_id)
            uow.commit()

    def test_implicit_rollback(
        self,
        in_memory_sqlite_session_factory: sessionmaker[Session],
        sample_paper: Paper,
    ) -> None:
        uow = SqlAlchemyUnitOfWork(in_memory_sqlite_session_factory)
        with uow:
            uow.papers.upsert_paper(sample_paper)

        with uow:
            retrieved_paper = uow.papers.get_paper(sample_paper.arxiv_id)
            assert retrieved_paper is None

    def test_explicit_rollback(
        self,
        in_memory_sqlite_session_factory: sessionmaker[Session],
        sample_paper: Paper,
    ) -> None:
        uow = SqlAlchemyUnitOfWork(in_memory_sqlite_session_factory)
        with uow:
            uow.papers.upsert_paper(sample_paper)
            uow.rollback()

        with uow:
            retrieved_paper = uow.papers.get_paper(sample_paper.arxiv_id)
            assert retrieved_paper is None

    def test_uow_session_lifecycle(self, in_memory_sqlite_session_factory: sessionmaker[Session]) -> None:
        uow = SqlAlchemyUnitOfWork(in_memory_sqlite_session_factory)
        assert not hasattr(uow, "session")

        with uow:
            assert uow.session is not None
            assert isinstance(uow.papers, SqlAlchemyPaperRepository)
