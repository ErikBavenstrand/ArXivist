from abc import ABC, abstractmethod

from arxivist.domain import model


class CategoryNotFoundError(Exception):
    """Exception raised when a category is not found in the repository."""

    def __init__(self, archive: str, subcategory: str | None) -> None:
        """Initializes the `CategoryNotFoundError` exception.

        Args:
            archive: The archive name.
            subcategory: The subcategory name.
        """
        super().__init__(f"Category with archive {archive!r} and subcategory {subcategory!r} not found.")


class PaperNotFoundError(Exception):
    """Exception raised when a paper is not found in the repository."""

    def __init__(self, arxiv_id: str) -> None:
        """Initializes the `PaperNotFoundError` exception.

        Args:
            arxiv_id: The ArXiv ID of the paper.
        """
        super().__init__(f"Paper with ArXiv ID {arxiv_id!r} not found.")


class AbstractPaperRepository(ABC):
    """Abstract `Paper` domain object repository."""

    @abstractmethod
    def upsert_category(self, category: model.Category) -> None:
        """Upserts a `Category` domain object into the database.

        Args:
            category: The `Category` domain object to add.
        """
        raise NotImplementedError

    @abstractmethod
    def get_category(self, archive: str, subcategory: str | None) -> model.Category | None:
        """Fetches a `Category` domain object from the database.

        Args:
            archive: The archive name.
            subcategory: The subcategory name.

        Returns:
            The `Category` domain object if found, otherwise `None`.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_category(self, archive: str, subcategory: str | None) -> None:
        """Deletes a `Category` domain object from the database.

        Args:
            archive: The archive name.
            subcategory: The subcategory name.

        Raises:
            CategoryNotFoundError: If the category is not found in the database.
        """
        raise NotImplementedError

    @abstractmethod
    def list_categories(self, limit: int) -> list[model.Category]:
        """Lists all `Category` domain objects in the database.

        Args:
            limit: The maximum number of categories to return.

        Returns:
            A list of `Category` domain objects.
        """
        raise NotImplementedError

    @abstractmethod
    def upsert_paper(self, paper: model.Paper) -> None:
        """Upserts a `Paper` domain object into the database.

        If any of the categories associated with the paper are missing in the database,
        they will be added. The paper itself will be updated or inserted as necessary.

        Args:
            paper: The `Paper` domain object to upsert.
        """
        raise NotImplementedError

    @abstractmethod
    def get_paper(self, arxiv_id: str) -> model.Paper | None:
        """Fetches a `Paper` domain object from the database.

        Args:
            arxiv_id: The ArXiv ID of the paper.

        Returns:
            The `Paper` domain object if found, otherwise `None`.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_paper(self, arxiv_id: str) -> None:
        """Deletes a `Paper` domain object from the database.

        Args:
            arxiv_id: The ArXiv ID of the paper.

        Raises:
            PaperNotFoundError: If the paper is not found in the database.
        """
        raise NotImplementedError

    @abstractmethod
    def list_papers(self, limit: int) -> list[model.Paper]:
        """Lists all `Paper` domain objects in the database.

        Args:
            limit: The maximum number of papers to return.

        Returns:
            A list of `Paper` domain objects.
        """
        raise NotImplementedError
