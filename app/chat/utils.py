import boto3
import openai
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
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


class RAGChain:
    def __init__(self) -> None:
        # OpenSearch index
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
        opensearch_index = OpenSearchVectorSearch(
            opensearch_url=f"https://{AWS_OPENSEARCH_HOST}",
            index_name="finance_data",
            embedding_function=embeddings,
            http_auth=auth,
            timeout=60,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )

        # RAG chain
        system_prompt = """
            You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer
            the question. If you don't know the answer, say that you
            don't know. Use three sentences maximum and keep the
            answer concise.
        
            {context}
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        llm = ChatAnthropic(
            model_name="claude-3-sonnet-20240229",
            api_key=SecretStr(ANTHROPIC_API_KEY),
            timeout=60,
            stop=None,
        )
        
        retriever = opensearch_index.as_retriever()
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
    def invoke(self, query: str):
        response = self.rag_chain.invoke({"input": query})
        return response["answer"]

rag_chain = RAGChain()


def get_rag_chain():
    return rag_chain
