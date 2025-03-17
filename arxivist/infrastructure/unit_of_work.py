from sqlalchemy.orm import Session, sessionmaker

from arxivist.application.ports.unit_of_work import AbstractUnitOfWork
from arxivist.infrastructure.repository import (
    SqlAlchemyPaperRepository,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """A `SQLAlchemy` Unit of Work for managing transactions."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initializes the `SqlAlchemyUnitOfWork`.

        Args:
            session_factory: The `SQLAlchemy` session factory.
        """
        self.session_factory = session_factory

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        """Enter the Unit of Work context.

        Returns:
            The Unit of Work.
        """
        self.session: Session = self.session_factory()
        self.papers = SqlAlchemyPaperRepository(self.session)
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Exit the Unit of Work context.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        if exc_type:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        """Commit the transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        self.session.rollback()
