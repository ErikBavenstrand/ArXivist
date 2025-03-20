from typing import Literal

import openai

from arxivist.application.ports.embedding_model import AbstractEmbeddingModel
from arxivist.infrastructure.exceptions import EmbeddingModelError


class OpenAIEmbeddingModel(AbstractEmbeddingModel):
    """OpenAI embedding model for converting strings to vectors using OpenAI API."""

    def __init__(
        self,
        client: openai.OpenAI,
        model: Literal["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"],
    ) -> None:
        """Initializes the `OpenAIEmbeddingModel` instance with the OpenAI client and model name.

        Args:
            client: The OpenAI client instance.
            model: The name of the OpenAI model to use for embedding.
        """
        self.client = client
        self.model = model

    def embed_string(self, text: str) -> list[float]:
        """Embeds a string into a list of floats using the OpenAI model.

        Args:
            text: The string to embed.

        Raises:
            EmbeddingModelError: If there is an error with the embedding request.

        Returns:
            A list of floats representing the embedded string.
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            error_msg = f"Error embedding string with OpenAI model {self.model!r}."
            raise EmbeddingModelError(error_msg) from e
