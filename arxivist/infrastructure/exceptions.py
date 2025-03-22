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
