from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
load_dotenv()

documents = SimpleDirectoryReader("./datasets").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("What type of data I am dealing with?")
print(response)
