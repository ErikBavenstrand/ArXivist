import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

from arxivist.domain import model


@dataclass
class VectorSearchFilter:
    """Technology-agnostic filter for vector search."""

    categories: list[model.Category] | None = None
    """List of categories to filter the search results by (AND operation)."""

    published_after: datetime.date | None = None
    """Date to filter the search results by, only papers published on or after this date will be included."""

    published_before: datetime.date | None = None
    """Date to filter the search results by, only papers published on or before this date will be included."""


class AbstractVectorRepository(ABC):
    """Abstract base class for a vector repository."""

    @abstractmethod
    def insert_embeddings(self, embeddings: list[list[float]], papers: list[model.Paper]) -> None:
        """Insert embeddings and metadata into the vector repository.

        Args:
            embeddings: List of embeddings to insert.
            papers: List of `Paper` domain objects corresponding to the embeddings.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_embeddings(self, arxiv_ids: list[str]) -> None:
        """Delete embeddings from the vector repository.

        Args:
            arxiv_ids: List of IDs of the embeddings to delete.
        """
        raise NotImplementedError

    @abstractmethod
    def query_embedding(
        self,
        query_embedding: list[float],
        top_k: int,
        filters: VectorSearchFilter | None,
    ) -> list[str]:
        """Query the vector repository for similar embeddings.

        Args:
            query_embedding: The embedding to query against.
            top_k: The number of similar embeddings to return.
            filters: Optional filters to apply to the query.

        Returns:
            List of metadata for the top_k similar embeddings.
        """
        raise NotImplementedError
