from abc import ABC, abstractmethod


class AbstractEmbeddingModel(ABC):
    """Abstract embedding model for converting strings to vectors."""

    @abstractmethod
    def embed_string(self, text: str) -> list[float]:
        """Embeds a string into a list of floats.

        Args:
            text: The string to embed.

        Returns:
            A list of floats representing the embedded string.
        """
        raise NotImplementedError
