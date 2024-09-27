import logging

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndexingPrepEvent(Event):
    documents: list[Document]


class IndexingEvent(Event):
    query_engine: BaseQueryEngine


class RagDataWorkflow(Workflow):
    @step
    async def ingest(self, ev: StartEvent) -> IndexingPrepEvent | None:
        logger.info("Ingest step started")
        documents: list[Document] | None = ev.get("documents")
        if documents is None:
            logger.warning("No documents provided")
            return None

        logger.info(f"Ingest {len(documents)} documents")
        return IndexingPrepEvent(documents=documents)

    @step
    async def index_and_store(self, ev: IndexingPrepEvent) -> IndexingEvent:
        logger.info(f"Indexing and storing started")
        documents: list[Document] = ev.documents
        index: VectorStoreIndex = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        logger.info("Index created successfully and query engine initialized")
        return IndexingEvent(query_engine=query_engine)

    @step
    async def finalize(self, ev: IndexingEvent) -> StopEvent:
        logger.info("Workflow finalized successfully with a valid query engine")
        return StopEvent(result=ev.query_engine)


# async def run_workflow(documents):
#     workflow = RagDataWorkflow()
#     result = await workflow.run(documents=documents)
#     return result


async def run_workflow():
    print("Running workflow")
    for _ in range(50):
        print(".")
    print("Workflow run.")
    return True
