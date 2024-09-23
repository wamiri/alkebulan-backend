import os

import openai
import qdrant_client
from qdrant_client.qdrant_client import QdrantClient


class SimilaritySearcher:
    def __init__(self) -> None:
        self.qdrant_client = QdrantClient(
            url=os.environ["QDRANT_API_URL"],
            api_key=os.environ["QDRANT_API_KEY"],
        )
        self.openai_client = openai.Client(api_key=os.environ["OPENAI_API_KEY"])

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
