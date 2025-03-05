# s1mc1ty/schema_analyzer.py
# pip install sqlalchemy

from sqlalchemy import inspect
from typing import Dict, List

class SchemaAnalyzer:
    def __init__(self, db_connector):
        self.inspector = db_connector.get_inspector()
        self.tables_info = {}
        self.foreign_keys = {}

    def analyze_structure(self):
        """Analyze database structure and store table metadata including column comments."""
        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            fks = self.inspector.get_foreign_keys(table_name)
            
            # Get column comments (PostgreSQL-specific)
            column_comments = {}
            with self.inspector.engine.connect() as conn:
                result = conn.execute(
                    "SELECT column_name, col_description("
                    f"(SELECT oid FROM pg_class WHERE relname = '{table_name}'), "
                    "ordinal_position - 1) "
                    "FROM information_schema.columns "
                    f"WHERE table_name = '{table_name}'"
                )
                column_comments = {row[0]: row[1] for row in result if row[1]}

            self.tables_info[table_name] = {
                'columns': {col['name']: {
                    'type': col['type'],
                    'comment': column_comments.get(col['name'])
                } for col in columns},
                'primary_key': self.inspector.get_pk_constraint(table_name)['constrained_columns']
            }
            self.foreign_keys[table_name] = fks

    def get_tables_info(self) -> Dict:
        return self.tables_info

    def get_foreign_keys(self) -> Dict:
        return self.foreign_keys