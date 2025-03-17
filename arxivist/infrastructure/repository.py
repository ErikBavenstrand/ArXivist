from sqlalchemy.orm import Session

from arxivist.application.ports.repository import (
    AbstractPaperRepository,
)
from arxivist.domain.paper import Category, Paper
from arxivist.infrastructure.orm import (
    CategoryORM,
    PaperORM,
)


class SqlAlchemyPaperRepository(AbstractPaperRepository):
    """A `Paper` domain object repository using `SQLAlchemy`."""

    def __init__(self, session: Session) -> None:
        """Initializes the `SqlAlchemyPaperRepository`.

        Args:
            session: The `SQLAlchemy` session.
        """
        self.session = session

    def add(self, paper: Paper) -> None:
        """Adds a `Paper` domain object to the repository.

        Args:
            paper: The `Paper` domain object to add.
        """
        paper_exists = self.get(paper.arxiv_id)
        if paper_exists:
            return

        self.session.add(self._to_orm(paper))

    def delete(self, arxiv_id: str) -> None:
        """Deletes a `Paper` domain object from the repository.

        Args:
            arxiv_id: The ArXiv ID of the paper to remove.
        """
        paper_orm = self.session.query(PaperORM).filter_by(arxiv_id=arxiv_id).first()
        if paper_orm:
            self.session.delete(paper_orm)

    def get(self, arxiv_id: str) -> Paper | None:
        """Gets a `Paper` domain object from the repository.

        Args:
            arxiv_id: The ArXiv ID of the paper to get.

        Returns:
            The `Paper` domain object if found, otherwise `None`.
        """
        paper_orm = self.session.query(PaperORM).filter_by(arxiv_id=arxiv_id).first()
        return self._to_paper(paper_orm) if paper_orm else None

    def list(self, limit: int | None = 50) -> list[Paper]:
        """Lists `Paper` domain objects from the repository.

        Args:
            limit: The maximum number of papers to list.

        Returns:
            A list of `Paper` domain objects.
        """
        orm_papers = (
            self.session.query(PaperORM)
            .order_by(PaperORM.published_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_paper(orm_paper) for orm_paper in orm_papers]

    @staticmethod
    def _to_orm(paper: Paper) -> PaperORM:
        """Converts a `Paper` domain object to a `PaperORM` ORM object.

        Args:
            paper: The `Paper` domain object to convert.

        Returns:
            The converted `PaperORM` ORM.
        """
        return PaperORM(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            abstract=paper.abstract,
            published_at=paper.published_at,
            categories={
                CategoryORM(major=category.major, minor=category.minor)
                for category in paper.categories
            },
        )

    @staticmethod
    def _to_paper(paper_orm: PaperORM) -> Paper:
        """Converts a `PaperORM` ORM object to a `Paper` domain object.

        Args:
            paper_orm: The `PaperORM` ORM object to convert.

        Returns:
            The converted `Paper` domain object.
        """
        return Paper(
            arxiv_id=paper_orm.arxiv_id,
            title=paper_orm.title,
            abstract=paper_orm.abstract,
            published_at=paper_orm.published_at,
            categories={
                Category(major=category.major, minor=category.minor)
                for category in paper_orm.categories
            },
        )
