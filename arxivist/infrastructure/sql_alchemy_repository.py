from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from arxivist.application.ports.repository import AbstractPaperRepository
from arxivist.domain import model
from arxivist.infrastructure.exceptions import CategoryNotFoundError, PaperNotFoundError
from arxivist.infrastructure.sql_alchemy_orm import CategoryORM, PaperORM


class SqlAlchemyPaperRepository(AbstractPaperRepository):
    """A `Paper` domain object repository using `SQLAlchemy`."""

    def __init__(self, session: Session) -> None:
        """Initializes the `SqlAlchemyPaperRepository`.

        Args:
            session: The `SQLAlchemy` session.
        """
        self.session = session

    def upsert_category(self, category: model.Category) -> None:
        """Upserts a `Category` domain object into the database.

        Args:
            category: The `Category` domain object to upsert.
        """
        category_orm = (
            self.session.query(CategoryORM)
            .filter(
                and_(
                    CategoryORM.archive == category.archive,
                    CategoryORM.subcategory.is_(None)
                    if category.subcategory is None
                    else CategoryORM.subcategory == category.subcategory,
                ),
            )
            .first()
        )
        if category_orm:
            category_orm.archive_name = category.archive_name
            category_orm.category_name = category.category_name
            category_orm.description = category.description
        else:
            self.session.add(self._to_category_orm(category))
        self.session.flush()

    def get_category(self, archive: str, subcategory: str | None) -> model.Category | None:
        """Fetches a `Category` domain object from the database.

        Args:
            archive: The archive name.
            subcategory: The subcategory name.

        Returns:
            The `Category` domain object if found, otherwise `None`.
        """
        category_orm = (
            self.session.query(CategoryORM)
            .filter(
                and_(
                    CategoryORM.archive == archive,
                    CategoryORM.subcategory.is_(None)
                    if subcategory is None
                    else CategoryORM.subcategory == subcategory,
                ),
            )
            .first()
        )
        return self._to_category(category_orm) if category_orm else None

    def delete_category(self, archive: str, subcategory: str | None) -> None:
        """Deletes a `Category` domain object from the database.

        Args:
            archive: The archive name.
            subcategory: The subcategory name.

        Raises:
            CategoryNotFoundError: If the category is not found in the database.
        """
        category_orm = (
            self.session.query(CategoryORM)
            .filter(
                and_(
                    CategoryORM.archive == archive,
                    CategoryORM.subcategory.is_(None)
                    if subcategory is None
                    else CategoryORM.subcategory == subcategory,
                ),
            )
            .first()
        )
        if not category_orm:
            raise CategoryNotFoundError(archive, subcategory)

        self.session.delete(category_orm)
        self.session.flush()

    def list_categories(self, limit: int = 50) -> list[model.Category]:
        """Lists all `Category` domain objects in the database.

        Args:
            limit: The maximum number of categories to return.

        Returns:
            A list of `Category` domain objects.
        """
        categories_orm = self.session.query(CategoryORM).order_by(CategoryORM.id).limit(limit).all()
        return [self._to_category(category_orm) for category_orm in categories_orm]

    def upsert_paper(self, paper: model.Paper) -> None:
        """Upserts a `Paper` domain object into the database.

        If any of the categories associated with the paper are missing in the database,
        they will be added. The paper itself will be updated or inserted as necessary.

        Args:
            paper: The `Paper` domain object to upsert.
        """
        existing_category_orms = (
            self.session.query(CategoryORM)
            .filter(
                or_(*[
                    and_(
                        CategoryORM.archive == category.archive,
                        CategoryORM.subcategory.is_(None)
                        if category.subcategory is None
                        else CategoryORM.subcategory == category.subcategory,
                    )
                    for category in paper.categories
                ]),
            )
            .all()
        )

        category_orms = existing_category_orms
        missing_categories = set(paper.categories) - {
            model.Category(archive=category_orm.archive, subcategory=category_orm.subcategory)
            for category_orm in existing_category_orms
        }
        if missing_categories:
            for category in missing_categories:
                category_orm = self._to_category_orm(category)
                self.session.add(category_orm)
                category_orms.append(category_orm)
            self.session.flush()

        paper_orm = self.session.query(PaperORM).filter_by(arxiv_id=paper.arxiv_id).first()
        if paper_orm:
            paper_orm.title = paper.title
            paper_orm.abstract = paper.abstract
            paper_orm.published_at = paper.published_at
            paper_orm.categories = category_orms
        else:
            self.session.add(self._to_paper_orm(paper, category_orms))
        self.session.flush()

    def get_paper(self, arxiv_id: str) -> model.Paper | None:
        """Fetches a `Paper` domain object from the database.

        Args:
            arxiv_id: The ArXiv ID of the paper.

        Returns:
            The `Paper` domain object if found, otherwise `None`.
        """
        paper_orm = self.session.query(PaperORM).filter_by(arxiv_id=arxiv_id).first()
        return self._to_paper(paper_orm) if paper_orm else None

    def delete_paper(self, arxiv_id: str) -> None:
        """Deletes a `Paper` domain object from the database.

        Args:
            arxiv_id: The ArXiv ID of the paper.

        Raises:
            PaperNotFoundError: If the paper is not found in the database.
        """
        paper_orm = self.session.query(PaperORM).filter_by(arxiv_id=arxiv_id).first()
        if not paper_orm:
            raise PaperNotFoundError(arxiv_id)

        self.session.delete(paper_orm)
        self.session.flush()

    def list_papers(self, limit: int = 50) -> list[model.Paper]:
        """Lists all `Paper` domain objects in the database.

        Args:
            limit: The maximum number of papers to return.

        Returns:
            A list of `Paper` domain objects.
        """
        papers_orm = self.session.query(PaperORM).order_by(PaperORM.id).limit(limit).all()
        return [self._to_paper(paper_orm) for paper_orm in papers_orm]

    @staticmethod
    def _to_category_orm(category: model.Category) -> CategoryORM:
        return CategoryORM(
            archive=category.archive,
            subcategory=category.subcategory,
            archive_name=category.archive_name,
            category_name=category.category_name,
            description=category.description,
        )

    @staticmethod
    def _to_category(category_orm: CategoryORM) -> model.Category:
        return model.Category(
            archive=category_orm.archive,
            subcategory=category_orm.subcategory,
            archive_name=category_orm.archive_name,
            category_name=category_orm.category_name,
            description=category_orm.description,
        )

    @staticmethod
    def _to_paper_orm(paper: model.Paper, category_orms: list[CategoryORM]) -> PaperORM:
        """Converts a `Paper` domain object to a `PaperORM` ORM object.

        Args:
            paper: The `Paper` domain object to convert.
            category_orms: The list of `CategoryORM` ORM objects associated with the paper.

        Returns:
            The converted `PaperORM` ORM.
        """
        return PaperORM(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            abstract=paper.abstract,
            published_at=paper.published_at,
            categories=category_orms,
        )

    @staticmethod
    def _to_paper(paper_orm: PaperORM) -> model.Paper:
        """Converts a `PaperORM` ORM object to a `Paper` domain object.

        Args:
            paper_orm: The `PaperORM` ORM object to convert.

        Returns:
            The converted `Paper` domain object.
        """
        return model.Paper(
            arxiv_id=paper_orm.arxiv_id,
            title=paper_orm.title,
            abstract=paper_orm.abstract,
            published_at=paper_orm.published_at,
            categories=[SqlAlchemyPaperRepository._to_category(category_orm) for category_orm in paper_orm.categories],
        )
