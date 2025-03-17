from abc import ABC, abstractmethod

from arxivist.domain.paper import Paper


class AbstractPaperRepository(ABC):
    """Abstract `Paper` domain object repository."""

    @abstractmethod
    def add(self, paper: Paper) -> None:
        """Adds a `Paper` domain object to the repository.

        Args:
            paper: The `Paper` domain object to add.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, arxiv_id: str) -> Paper | None:
        """Gets a `Paper` domain object from the repository.

        Args:
            arxiv_id: The ArXiv ID of the paper to get.

        Returns:
            The `Paper` domain object if found, otherwise `None`.
        """
        raise NotImplementedError

    @abstractmethod
    def list(self, limit: int | None) -> list[Paper]:
        """Lists `Paper` domain objects from the repository.

        Args:
            limit: The maximum number of papers to list.

        Returns:
            A list of `Paper` domain objects.
        """
        raise NotImplementedError
