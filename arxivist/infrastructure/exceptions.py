class RSSParsingError(Exception):
    """Exception raised when RSS parsing fails."""


class ArXivRSSMissingFieldError(Exception):
    """Exception raised when a required field is missing in the ArXiv RSS feed."""

    def __init__(self, field_name: str) -> None:
        """Initializes the `ArXivRSSMissingFieldError` exception.

        Args:
            field_name: The name of the missing field.
        """
        super().__init__(f"Missing required field {field_name!r} in the RSS feed entry.")


class EmbeddingModelError(Exception):
    """Exception raised when there is an error with the embedding model."""


class VectoryRepositoryInsertionError(Exception):
    """Exception raised when there is an error inserting embeddings into the vector repository."""


class VectoryRepositoryQueryError(Exception):
    """Exception raised when there is an error querying the vector repository."""


class RepositoryError(Exception):
    """Exception raised when there is an error with the SQLAlchemy repository."""


class CategoryNotFoundError(RepositoryError):
    """Exception raised when a category is not found in the repository."""

    def __init__(self, archive: str, subcategory: str | None) -> None:
        """Initializes the `CategoryNotFoundError` exception.

        Args:
            archive: The archive name.
            subcategory: The subcategory name.
        """
        super().__init__(f"Category with archive {archive!r} and subcategory {subcategory!r} not found.")


class PaperNotFoundError(RepositoryError):
    """Exception raised when a paper is not found in the repository."""

    def __init__(self, arxiv_id: str) -> None:
        """Initializes the `PaperNotFoundError` exception.

        Args:
            arxiv_id: The ArXiv ID of the paper.
        """
        super().__init__(f"Paper with ArXiv ID {arxiv_id!r} not found.")
