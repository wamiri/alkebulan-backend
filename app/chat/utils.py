import boto3
from numpy import gcd
import openai
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from openai.types import CreateEmbeddingResponse
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from pydantic import SecretStr
from qdrant_client import QdrantClient
from requests_aws4auth import AWS4Auth

from app.chat.config import (
    ANTHROPIC_API_KEY,
    AWS_ACCESS_KEY_ID,
    AWS_OPENSEARCH_HOST,
    AWS_OPENSEARCH_REGION,
    AWS_SECRET_ACCESS_KEY,
    OPENAI_API_KEY,
    QDRANT_API_KEY,
    QDRANT_API_URL,
)


class SimilaritySearcher:
    def __init__(self) -> None:
        self.qdrant_client = QdrantClient(
            url=QDRANT_API_URL,
            api_key=QDRANT_API_KEY,
        )
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)

    def similarity_search(self, text):
        embeddings = (
            self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text,
            )
            .data[0]
            .embedding
        )
        results = self.qdrant_client.search(
            collection_name="winter_sports",
            query_vector=embeddings,
            limit=5,
        )

        return results


similarity_searcher = SimilaritySearcher()


def get_similarity_searcher():
    return similarity_searcher


class OpenSearcher:
    def __init__(self, index_name: str = "new_finance_index") -> None:
        host = AWS_OPENSEARCH_HOST
        region = AWS_OPENSEARCH_REGION
        service = "es"
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, region, service)
        self.opensearch_client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )
        self.index_name = index_name
        self.embedding_model = "text-embedding-ada-002"
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)

    def _get_query_embedding(self, query: str):
        return self.openai_client.embeddings.create(
            input=query,
            model=self.embedding_model,
        )

    def _get_kNN_vector_search(self, embeddings: CreateEmbeddingResponse, top_k: int):
        response = self.opensearch_client.search(
            index=self.index_name,
            body={
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": embeddings.data[0].embedding,
                            "k": top_k,
                        }
                    }
                },
            },
        )
        summaries = [hit["_source"]["text_segment"] for hit in response["hits"]["hits"]]
        return summaries

    def search_documents(self, query: str, top_k: int = 5):
        embeddings = self._get_query_embedding(query)
        response = self._get_kNN_vector_search(embeddings, top_k)
        combined_text = "\n".join(response)

        summary = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Answer the following question: {query} using the following text: {combined_text}",
                },
            ],
        )

        choices = summary.choices
        return choices[0].message.content


open_searcher = OpenSearcher()


def get_open_searcher():
    return open_searcher


class RAGChain:
    def __init__(self) -> None:
        embeddings = OpenAIEmbeddings(api_key=SecretStr(OPENAI_API_KEY))
        service = "es"
        region = AWS_OPENSEARCH_REGION
        credentials = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        ).get_credentials()

        auth = AWS4Auth(
            AWS_ACCESS_KEY_ID,
            AWS_SECRET_ACCESS_KEY,
            region,
            service,
            session_token=credentials.token,
        )

        self.index_name = "new_finance_index"
        self.vector_store = OpenSearchVectorSearch(
            opensearch_url=f"https://{AWS_OPENSEARCH_HOST}",
            embedding_function=embeddings,
            http_auth=auth,
            timeout=60,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            index_name=self.index_name,
        )

    def query(self, query: str):
        return self.vector_store.similarity_search(
            query, k=10, search_type="approximate_search", vector_field="vector_field"
        )


rag_chain = RAGChain()


def get_rag_chain():
    return rag_chain
