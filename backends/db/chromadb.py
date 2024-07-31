from langchain_community.vectorstores import Chroma


class ChromaDBConnectionManager:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init__()
        return cls.__instance

    def __init__(self):
        self.clients = {}

    def get_connection(self, db_name, **kwargs):
        if db_name in self.clients:
            return self.clients[db_name]
        else:
            self.clients[db_name] = Chroma(**kwargs)
            return self.clients[db_name]