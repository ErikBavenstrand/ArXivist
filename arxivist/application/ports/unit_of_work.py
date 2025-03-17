from abc import ABC, abstractmethod

from arxivist.application.ports.repository import AbstractPaperRepository


class AbstractUnitOfWork(ABC):
    """Abstract Unit of Work for managing transactions."""

    papers: AbstractPaperRepository
    """A `Paper` domain object repository."""

    def __enter__(self) -> "AbstractUnitOfWork":
        """Enter the Unit of Work context.

        Returns:
            The Unit of Work.
        """
        return self

    def __exit__(self, *args) -> None:
        """Exit the Unit of Work context.

        Args:
            args: The arguments passed to the `__exit__` method.
        """
        self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError
