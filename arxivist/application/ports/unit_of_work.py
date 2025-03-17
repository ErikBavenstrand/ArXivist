from abc import ABC, abstractmethod

from arxivist.application.ports.repositories import (
    AbstractPaperRepository,
)


class AbstractUnitOfWork(ABC):
    """Abstract Unit of Work for managing transactions."""

    papers: AbstractPaperRepository
    """A `Paper` domain object repository."""

    @abstractmethod
    def __enter__(self) -> "AbstractUnitOfWork":
        """Enter the Unit of Work context.

        Returns:
            The Unit of Work.
        """
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Exit the Unit of Work context.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError
