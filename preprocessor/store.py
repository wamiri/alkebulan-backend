from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import requests
import base64
import openai


class ElasticCloudEmbeddingStore:
    def __init__(
        self,
        cloud_id,
        es_api_key,
        open_api_key,
        index_name="finance_data_embeddings",
    ):
        self.cloud_id = cloud_id
        self.index_name = index_name
        self.model = ("text-embedding-ada-002",)
        self.es_client = Elasticsearch(cloud_id=cloud_id, api_key=es_api_key)
        self.openai_client = openai.Client(api_key=open_api_key)

        if not self.indexExists():
            self.es_client.create(index=self.index_name, ignore=400)

    def indexExists(self):
        return self.es_client.indices.exists(index=self.index_name)

    # Store converted table dfs in elastic
    def storeDataframe(self, df, table_id):
        # Define the mapping based on the DataFrame schema
        mapping = {
            "properties": {
                col: {"type": self.getElasticSearchType(df[col].dtype)}
                for col in df.columns
            }
        }

        # Put the mapping in Elasticsearch
        if not self.es_client.indices.get_mapping(index=self.index_name):
            self.es_client.indices.put_mapping(index=self.index_name, body=mapping)

        # Insert the DataFrame rows into the Elasticsearch index
        actions = []
        for index, row in df.iterrows():
            doc = row.to_dict()
            doc["table_id"] = table_id
            doc["row_id"] = index
            action = {"_index": self.index_name, "_source": doc}
            actions.append(action)

        success, _ = bulk(self.es_client, actions)
        return success

    # Helper function to map Pandas data types to Elasticsearch types
    def getElasticSearchType(dtype):
        if dtype == object:
            return "text"
        elif dtype == int:
            return "integer"
        elif dtype == float:
            return "float"
        else:
            return "text"

    def createVectorEmbeddings(self, text):
        return self.openai_client.embeddings.create(model=self.model, input=text)

    def storeTextEmbeddings(self, textChunks, index_name):
        for chunk in textChunks:
            vectorEmbeddings = self.createVectorEmbeddings(chunk)

            if not self.es_client.indices.get_mapping(index=self.index_name):
                self.es_client.indices.put_mapping(
                    index=self.index_name, body=self.getTextMapping()
                )

            # Store the embedding along with the text and its position in Elasticsearch
            self.es_client.index(
                index=index_name,
                body={
                    "text_segment": chunk,
                    "embedding": vectorEmbeddings.data[0].embedding,
                    "metadata": chunk.metadata,
                },
            )

    def getTextMapping():
        return {
            "mappings": {
                "properties": {
                    "text_segment": {"type": "text"},
                    "embedding": {
                        "type": "dense_vector",  # For storing embeddings as vectors
                        "dims": 1536,  # Number of dimensions
                    },
                    "metadata": {
                        "properties": {
                            "filename": {"type": "keyword"},
                            "filetype": {"type": "keyword"},
                            "page_number": {"type": "integer"},
                            "last_modified": {
                                "type": "date",
                                "format": "yyyy-MM-dd'T'HH:mm:ss",  # ISO date format
                            },
                            "languages": {
                                "type": "keyword"  # Can store multiple languages as an array of strings
                            },
                            "orig_elements": {"type": "text"},
                        }
                    },
                }
            }
        }
