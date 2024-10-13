import boto3
import openai
import requests
from flashrank import Ranker, RerankRequest
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from numpy import gcd
from openai.types import CreateEmbeddingResponse
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from pydantic import SecretStr
from qdrant_client import QdrantClient
from requests_aws4auth import AWS4Auth

from app.rag.config import (
    ANTHROPIC_API_KEY,
    AWS_ACCESS_KEY_ID,
    AWS_OPENSEARCH_HOST,
    AWS_OPENSEARCH_REGION,
    AWS_SECRET_ACCESS_KEY,
    OPENAI_API_KEY,
    QDRANT_API_KEY,
    QDRANT_API_URL,
)


class OpenSearchVectorStore:
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
        combined_text = "\n\n".join(response)

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


class OpenSearchVectorStoreLangChain:
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

        self.finance_index_vector_store = OpenSearchVectorSearch(
            opensearch_url=f"https://{AWS_OPENSEARCH_HOST}",
            embedding_function=embeddings,
            http_auth=auth,
            timeout=60,
            use_ssl=True,
            verify_certs=True,
            http_compress=True,
            connection_class=RequestsHttpConnection,
            index_name="new_finance_index",
        )

        self.table_index_vector_store = OpenSearchVectorSearch(
            opensearch_url=f"https://{AWS_OPENSEARCH_HOST}",
            embedding_function=embeddings,
            http_auth=auth,
            timeout=60,
            use_ssl=True,
            verify_certs=True,
            http_compress=True,
            connection_class=RequestsHttpConnection,
            index_name="ngx_tables",
        )

        self.ranker = Ranker(max_length=1024)

    def _get_documents_from_finance_index(self, query):
        return self.finance_index_vector_store.similarity_search(
            query,
            search_type="script_scoring",
            space_type="cosinesimil",
            vector_field="embedding",
            text_field="text_segment",
            metadata_field="metadata",
        )

    def _get_documents_from_table_index(self, query):
        return self.table_index_vector_store.similarity_search(
            query,
            search_type="script_scoring",
            space_type="cosinesimil",
            vector_field="embedding",
            text_field="text",
            metadata_field="metadata",
        )

    def get_documents(self, query: str):
        finance_index_documents = self._get_documents_from_finance_index(query)
        table_index_documents = self._get_documents_from_table_index(query)

        return finance_index_documents + table_index_documents

    def rerank(self, query, documents, top_k=10):
        passages = list()
        for i, document in enumerate(documents):
            passage = {
                "id": i + 1,
                "text": document.page_content,
                "meta": {"filename": document.metadata["filename"]},
            }
            passages.append(passage)

        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        return results[:top_k]

    def rag(self, query):
        llm = ChatAnthropic(
            api_key=SecretStr(ANTHROPIC_API_KEY),
            model_name="claude-3-sonnet-20240229",
            timeout=None,
            stop=None,
        )

        system_prompt = (
            "Using the following information provided below, please answer the user's query.\
                         If the information is not sufficient to answer the query, please say so.\
                         Include the filename in the response.\
                         Relevant information:\n"
        )

        documents = self.get_documents(query)
        reranked_documents = self.rerank(query, documents)

        for i, document in enumerate(reranked_documents):
            document_information = f"{i + 1}. Filename: {document['meta']['filename']} Text: {document['text']}\n"
            system_prompt += document_information

        user_prompt = f"User query: {query}"

        messages = [("system", system_prompt), ("human", user_prompt)]
        response = llm.invoke(messages)

        return response.json()


class QDrantVectorStore:
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
