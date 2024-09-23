class QueryEngine:
    def __init__(self) -> None:
        self.engine = None

    def set_engine(self, query_engine):
        self.engine = query_engine

    def query(self, prompt):
        if self.engine is None:
            return "Query engine not set"

        return self.engine.query(prompt)


query_engine = QueryEngine()


def get_query_engine():
    return query_engine
