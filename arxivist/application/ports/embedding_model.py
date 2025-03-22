from abc import ABC, abstractmethod
from typing import overload


class AbstractEmbeddingModel(ABC):
    """Abstract embedding model for converting strings to vectors."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Get the dimensions of the embedding model.

        Returns:
            The number of dimensions for the embedding model.
        """
        raise NotImplementedError

    @overload
    def embed_string(self, text: str) -> list[float]: ...

    @overload
    def embed_string(self, text: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def embed_string(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """Embeds a string into an embedding using the model.

        Args:
            text: The string or list of strings to embed.

        Returns:
            A list of floats representing the embedded string or a list of lists of floats
            if multiple strings are provided.
        """
        raise NotImplementedError
