class QueryEngine:
    def __init__(self) -> None:
        # self.engine = None
        self.engine = False

    def set_engine(self, query_engine):
        self.engine = query_engine

    def query(self, prompt):
        # if self.engine is None:
        #     return "Query engine not set"
        if not self.engine:
            return "Query engine not set"

        # return self.engine.query(prompt)
        return len(prompt)


query_engine = QueryEngine()


def get_query_engine():
    return query_engine
