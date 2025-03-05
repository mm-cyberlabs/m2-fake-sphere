# s1mc1ty/db_connector.py
# pip install sqlalchemy psycopg2-binary

from sqlalchemy import create_engine, inspect

class DatabaseConnector:
    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.engine = create_engine(f"{connection_string}/{database_name}")
        self.inspector = inspect(self.engine)

    def get_engine(self):
        return self.engine

    def get_inspector(self):
        return self.inspector