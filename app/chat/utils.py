import boto3
from numpy import gcd
import openai
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
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
    def __init__(self) -> None:
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
        self.index_name = "finance_data"
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)

    def _get_query_embedding(self, query: str):
        return self.openai_client.embeddings.create(
            input=query,
            model="text-embedding-ada-002",
        )

    def _get_kNN_vector_search(self, embeddings: CreateEmbeddingResponse):
        response = self.opensearch_client.search(
            index=self.index_name,
            body={
                "size": 2,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": embeddings.data[0].embedding,
                            "k": 10,
                        }
                    }
                },
            },
        )
        top_hit_summary = response["hits"]["hits"][0]["_source"]["text"]
        return top_hit_summary

    def search_documents(self, query: str):
        embeddings = self._get_query_embedding(query)
        response = self._get_kNN_vector_search(embeddings)
        summary = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Answer the following question:"
                    + query
                    + "by using the following text:"
                    + response,
                },
            ],
        )

        choices = summary.choices
        return choices


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

        self.index_name = "finance_data"
        self.vector_field = "embedding"

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

        index_body = {
            "settings": {"index.knn": True},
            "mappings": {
                "properties": {
                    "vector_field": {
                        "type": "knn_vector",
                        "dimension": 1536,
                        "method": {
                            "engine": "faiss",
                            "name": "hnsw",
                            "space_type": "l2",
                        },
                    }
                }
            },
        }
        if not self.vector_store.client.indices.exists(index=self.index_name):
            response = self.vector_store.client.create(self.index_name, body=index_body, id=1)
            print(response)

    def query(self, query: str):
        return self.vector_store.similarity_search(
            query,
            vector_field=self.vector_field,
            text_field="text",
            metadata_field="metadata",
            search_type="approximate_search",
        )


rag_chain = RAGChain()


def get_rag_chain():
    return rag_chain
