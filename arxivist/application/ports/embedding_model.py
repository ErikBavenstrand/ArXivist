from abc import ABC, abstractmethod


class AbstractEmbeddingModel(ABC):
    """Abstract embedding model for converting strings to vectors."""

    @abstractmethod
    def embed_string(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """Embeds a string into a list of floats.

        Args:
            text: The string or list of strings to embed.

        Returns:
            A list of floats representing the embedded string or a list of lists of floats
            if multiple strings are provided.
        """
        raise NotImplementedError
