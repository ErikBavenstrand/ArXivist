from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arxivist import config
from arxivist.application.ports.unit_of_work import AbstractUnitOfWork
from arxivist.infrastructure.repository import (
    SqlAlchemyPaperRepository,
)

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.DATABASE_URL,
        isolation_level="REPEATABLE READ",
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """A `SQLAlchemy` Unit of Work for managing transactions."""

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY) -> None:
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

    def __exit__(self, *args) -> None:
        """Exit the Unit of Work context.

        Args:
            args: The arguments passed to the `__exit__` method.
        """
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        self.session.rollback()
