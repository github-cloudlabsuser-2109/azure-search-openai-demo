# Import necessary libraries and modules
import os
from abc import ABC
from dataclasses import dataclass
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    List,github-cloudlabsuser-2109
    Optional,
    TypedDict,
    cast,
)
from urllib.parse import urljoin

import aiohttp
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import (
    QueryCaptionResult,
    QueryType,
    VectorizedQuery,
    VectorQuery,
)
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from core.authentication import AuthenticationHelper
from text import nonewlines

# Define a dataclass for Document
@dataclass
class Document:
    # Define the attributes of the Document class
    id: Optional[str]
    content: Optional[str]
    embedding: Optional[List[float]]
    image_embedding: Optional[List[float]]
    category: Optional[str]
    sourcepage: Optional[str]
    sourcefile: Optional[str]
    oids: Optional[List[str]]
    groups: Optional[List[str]]
    captions: List[QueryCaptionResult]
    score: Optional[float] = None
    reranker_score: Optional[float] = None

    # Define a method to serialize the Document object for results
    def serialize_for_results(self) -> dict[str, Any]:
        ...

    # Define a class method to trim the embedding
    @classmethod
    def trim_embedding(cls, embedding: Optional[List[float]]) -> Optional[str]:
        ...

# Define a dataclass for ThoughtStep
@dataclass
class ThoughtStep:
    title: str
    description: Optional[Any]
    props: Optional[dict[str, Any]] = None

# Define an abstract base class for Approach
class Approach(ABC):
    # Define the constructor for the Approach class
    def __init__(
        self,
        search_client: SearchClient,
        openai_client: AsyncOpenAI,
        auth_helper: AuthenticationHelper,
        query_language: Optional[str],
        query_speller: Optional[str],
        embedding_deployment: Optional[str],  # Not needed for non-Azure OpenAI or for retrieval_mode="text"
        embedding_model: str,
        embedding_dimensions: int,
        openai_host: str,
        vision_endpoint: str,
        vision_token_provider: Callable[[], Awaitable[str]],
    ):
        ...

    # Define a method to build a filter
    def build_filter(self, overrides: dict[str, Any], auth_claims: dict[str, Any]) -> Optional[str]:
        ...

    # Define an asynchronous method to perform a search
    async def search(
        self,
        top: int,
        query_text: Optional[str],
        filter: Optional[str],
        vectors: List[VectorQuery],
        use_text_search: bool,
        use_vector_search: bool,
        use_semantic_ranker: bool,
        use_semantic_captions: bool,
        minimum_search_score: Optional[float],
        minimum_reranker_score: Optional[float],
    ) -> List[Document]:
        ...

    # Define a method to get the content of the sources
    def get_sources_content(
        self, results: List[Document], use_semantic_captions: bool, use_image_citation: bool
    ) -> list[str]:
        ...

    # Define a method to get a citation
    def get_citation(self, sourcepage: str, use_image_citation: bool) -> str:
        ...

    # Define an asynchronous method to compute the text embedding
    async def compute_text_embedding(self, q: str):
        ...

    # Define an asynchronous method to compute the image embedding
    async def compute_image_embedding(self, q: str):
        ...

    # Define an asynchronous method to run the approach
    async def run(
        self,
        messages: list[ChatCompletionMessageParam],
        session_state: Any = None,
        context: dict[str, Any] = {},
    ) -> dict[str, Any]:
        ...

    # Define an asynchronous method to run the approach in a stream
    async def run_stream(
        self,
        messages: list[ChatCompletionMessageParam],
        session_state: Any = None,
        context: dict[str, Any] = {},
    ) -> AsyncGenerator[dict[str, Any], None]:
        ...