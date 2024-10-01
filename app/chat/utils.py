import openai
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from qdrant_client.qdrant_client import QdrantClient

from app.chat.config import (
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
        host = "search-opensearch-ua7tve3svne673wdtaalcuwsae.us-east-1.es.amazonaws.com"
        region = "us-east-1"
        service = "es"
        credentials = boto3.Session().get_credentials()

        auth = AWSV4SignerAuth(credentials, region, service)
        self.client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )
        self.index_name = "finance_data"

    def search_documents(self, query):
        q = {"size": 10, "query": {"multi_match": {"query": query}}}
        return self.client.search(body=q, index=self.index_name)


open_searcher = OpenSearcher()


def get_open_searcher():
    return open_searcher
