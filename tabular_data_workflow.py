import asyncio

from dotenv import load_dotenv
from llama_index.core import Document, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI

load_dotenv()


class ColumnExtractionPrepEvent(Event):
    index: VectorStoreIndex


class ColumnExtractionEvent(Event):
    columns: str


class TabularDataWorkflow(Workflow):
    @step
    async def ingest(self, ev: StartEvent) -> ColumnExtractionPrepEvent | None:
        documents: list[Document] | None = ev.get("documents")
        if documents is None:
            return None
        index: VectorStoreIndex = VectorStoreIndex.from_documents(documents)
        return ColumnExtractionPrepEvent(index=index)

    @step
    async def extract_columns(
        self,
        ev: ColumnExtractionPrepEvent,
    ) -> StopEvent:
        index: VectorStoreIndex = ev.index

        query_engine = index.as_query_engine()
        result = await query_engine.aquery(
            """
            What type of data am I dealing with and get me a list of all the columns in the data?
            """
        )
        return StopEvent(result=result)


async def main():
    documents = SimpleDirectoryReader("./data").load_data()
    workflow = TabularDataWorkflow()
    result = await workflow.run(documents=documents)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
