import openai
import openai.resources
import pytest

from arxivist.infrastructure.exceptions import EmbeddingModelError
from arxivist.infrastructure.openai_embedding_model import OpenAIEmbeddingModel


class FakeOpenAIClient(openai.OpenAI):
    def __init__(self, return_value: list[list[float]] | None = None, *, raise_error: bool = False) -> None:
        self.return_value = return_value or [[0.1, 0.2, 0.3]]
        self.raise_error = raise_error
        self.embeddings = FakeOpenAIEmbeddings(self.return_value, raise_error=self.raise_error)


class FakeOpenAIEmbeddings(openai.resources.Embeddings):
    def __init__(self, return_value: list[list[float]], *, raise_error: bool) -> None:
        self.return_value = return_value
        self.raise_error = raise_error

    def create(self, *args, **kwargs) -> openai.types.CreateEmbeddingResponse:
        if self.raise_error:
            raise openai.OpenAIError("API error")
        return openai.types.CreateEmbeddingResponse(
            data=[
                openai.types.Embedding(
                    embedding=emb,
                    index=i,
                    object="embedding",
                )
                for i, emb in enumerate(self.return_value)
            ],
            object="list",
            model="text-embedding-ada-002",
            usage=openai.types.create_embedding_response.Usage(
                prompt_tokens=0,
                total_tokens=0,
            ),
        )


class TestOpenAIEmbeddingModel:
    def test_openai_embedding_model_single(self) -> None:
        fake_client = FakeOpenAIClient(return_value=[[0.1, 0.2, 0.3]])

        model = OpenAIEmbeddingModel(
            client=fake_client,
            model="text-embedding-ada-002",
        )
        text = "This is a test string."
        embedding = model.embed_string(text)
        assert embedding == [0.1, 0.2, 0.3]

    def test_openai_embedding_model_multiple(self) -> None:
        fake_client = FakeOpenAIClient(return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        model = OpenAIEmbeddingModel(
            client=fake_client,
            model="text-embedding-ada-002",
        )
        texts = ["This is a test string.", "This is another test string."]
        embeddings = model.embed_string(texts)
        assert embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    def test_openai_embedding_model_dimensions(self) -> None:
        fake_client = FakeOpenAIClient(return_value=[[0.1, 0.2, 0.3]])

        model = OpenAIEmbeddingModel(
            client=fake_client,
            model="text-embedding-ada-002",
        )
        dimensions = model.dimensions
        assert dimensions == 3

    def test_openai_embedding_model_error(self) -> None:
        fake_client = FakeOpenAIClient(raise_error=True)

        model = OpenAIEmbeddingModel(
            client=fake_client,
            model="text-embedding-ada-002",
        )
        text = "This is a test string."

        with pytest.raises(
            EmbeddingModelError,
            match="Error embedding string with OpenAI model 'text-embedding-ada-002'",
        ):
            model.embed_string(text)
