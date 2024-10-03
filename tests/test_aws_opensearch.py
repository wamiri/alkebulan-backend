import os

import boto3
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from opensearchpy import OpenSearch, RequestsHttpConnection
from pydantic import SecretStr
from requests_aws4auth import AWS4Auth

load_dotenv()

embeddings = OpenAIEmbeddings(api_key=SecretStr(os.environ["OPENAI_API_KEY"]))

service = "es"
region = os.environ["AWS_OPENSEARCH_REGION"]
credentials = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
).get_credentials()
auth = AWS4Auth(
    os.environ["AWS_ACCESS_KEY_ID"],
    os.environ["AWS_SECRET_ACCESS_KEY"],
    region,
    service,
    session_token=credentials.token,
)

searcher = OpenSearchVectorSearch(
    opensearch_url=f"https://{os.environ['AWS_OPENSEARCH_HOST']}",
    index_name="finance_data",
    embedding_function=embeddings,
    http_auth=auth,
    timeout=60,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

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
    api_key=SecretStr(os.environ["ANTHROPIC_API_KEY"]),
    timeout=60,
    stop=None,
)
retriever = searcher.as_retriever()
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

response = rag_chain.invoke({"input": "What are the documents about?"})
print(response["answer"])
