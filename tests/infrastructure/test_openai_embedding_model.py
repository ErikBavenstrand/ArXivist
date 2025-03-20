from unittest.mock import MagicMock

import openai
import pytest

from arxivist.infrastructure.exceptions import EmbeddingModelError
from arxivist.infrastructure.openai_embedding_model import OpenAIEmbeddingModel


class TestOpenAIEmbeddingModel:
    def test_openai_embedding_model(self) -> None:
        mock_openai_client = MagicMock(openai.OpenAI)
        mock_openai_client.embeddings = MagicMock()
        mock_openai_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[0.1, 0.2, 0.3])],
        )

        model = OpenAIEmbeddingModel(
            client=mock_openai_client,
            model="text-embedding-ada-002",
        )
        text = "This is a test string."
        embedding = model.embed_string(text)
        assert embedding == [0.1, 0.2, 0.3]

    def test_openai_embedding_model_error(self) -> None:
        mock_openai_client = MagicMock(openai.OpenAI)
        mock_openai_client.embeddings = MagicMock()
        mock_openai_client.embeddings.create.side_effect = Exception("API error")

        model = OpenAIEmbeddingModel(
            client=mock_openai_client,
            model="text-embedding-ada-002",
        )
        text = "This is a test string."

        with pytest.raises(
            EmbeddingModelError,
            match="Error embedding string with OpenAI model 'text-embedding-ada-002'",
        ):
            model.embed_string(text)
