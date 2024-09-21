import asyncio

from dotenv import load_dotenv
from llama_index.core import Document, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.llms.openai import OpenAI

load_dotenv()


class IndexingPrepEvent(Event):
    documents: list[Document]


class IndexingEvent(Event):
    query_engine: BaseQueryEngine


class RagDataWorkflow(Workflow):
    @step
    async def ingest(self, ev: StartEvent) -> IndexingPrepEvent | None:
        documents: list[Document] | None = ev.get("documents")

        if documents is None:
            return None

        return IndexingPrepEvent(documents=documents)

    @step
    async def index_and_store(self, ev: IndexingPrepEvent) -> IndexingEvent:
        documents: list[Document] = ev.documents
        index: VectorStoreIndex = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        return IndexingEvent(query_engine=query_engine)

    @step
    async def finalize(self, ev: IndexingEvent) -> StopEvent:
        return StopEvent(result=ev.query_engine)


async def run_workflow(documents):
    workflow = RagDataWorkflow()
    result = await workflow.run(documents=documents)
    return result
