"""
Relationship Mapper
This module detects and maps foreign key relationships between database tables.
"""

from typing import List, Dict, Any, Tuple
import psycopg2
import logging

logger = logging.getLogger(__name__)


class RelationshipMapper:
    """
    Maps foreign key relationships between database tables.
    """

    def __init__(self, connection_manager):
        """
        Initialize the relationship mapper.

        Args:
            connection_manager: DatabaseConnectionManager instance
        """
        self.connection_manager = connection_manager

    def get_foreign_key_relationships(self, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all foreign key relationships for a specific table.

        Args:
            schema_name: Name of the schema
            table_name: Name of the table

        Returns:
            List of dictionaries containing foreign key relationship details
        """
        query = """
                SELECT tc.constraint_name, \
                       tc.table_schema  AS source_schema, \
                       tc.table_name    AS source_table, \
                       kcu.column_name  AS source_column, \
                       ccu.table_schema AS target_schema, \
                       ccu.table_name   AS target_table, \
                       ccu.column_name  AS target_column
                FROM information_schema.table_constraints AS tc
                         JOIN information_schema.key_column_usage AS kcu
                              ON tc.constraint_name = kcu.constraint_name
                                  AND tc.table_schema = kcu.table_schema
                         JOIN information_schema.constraint_column_usage AS ccu
                              ON ccu.constraint_name = tc.constraint_name
                                  AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = %s
                  AND tc.table_name = %s
                ORDER BY tc.constraint_name, kcu.ordinal_position; \
                """

        connection = self.connection_manager.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (schema_name, table_name))
                relationships = []

                for row in cursor.fetchall():
                    relationship = {
                        'constraint_name': row[0],
                        'source_schema': row[1],
                        'source_table': row[2],
                        'source_column': row[3],
                        'target_schema': row[4],
                        'target_table': row[5],
                        'target_column': row[6]
                    }
                    relationships.append(relationship)

                logger.debug(f"Found {len(relationships)} foreign keys for {schema_name}.{table_name}")
                return relationships
        finally:
            self.connection_manager.release_connection(connection)

    def get_reverse_relationships(self, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all tables that reference the specified table (reverse foreign keys).

        Args:
            schema_name: Name of the schema
            table_name: Name of the table

        Returns:
            List of dictionaries containing reverse relationship details
        """
        query = """
                SELECT tc.constraint_name, \
                       tc.table_schema  AS referencing_schema, \
                       tc.table_name    AS referencing_table, \
                       kcu.column_name  AS referencing_column, \
                       ccu.table_schema AS referenced_schema, \
                       ccu.table_name   AS referenced_table, \
                       ccu.column_name  AS referenced_column
                FROM information_schema.table_constraints AS tc
                         JOIN information_schema.key_column_usage AS kcu
                              ON tc.constraint_name = kcu.constraint_name
                                  AND tc.table_schema = kcu.table_schema
                         JOIN information_schema.constraint_column_usage AS ccu
                              ON ccu.constraint_name = tc.constraint_name
                                  AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND ccu.table_schema = %s
                  AND ccu.table_name = %s
                ORDER BY tc.table_schema, tc.table_name, tc.constraint_name; \
                """

        connection = self.connection_manager.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (schema_name, table_name))
                relationships = []

                for row in cursor.fetchall():
                    relationship = {
                        'constraint_name': row[0],
                        'referencing_schema': row[1],
                        'referencing_table': row[2],
                        'referencing_column': row[3],
                        'referenced_schema': row[4],
                        'referenced_table': row[5],
                        'referenced_column': row[6]
                    }
                    relationships.append(relationship)

                logger.debug(f"Found {len(relationships)} tables referencing {schema_name}.{table_name}")
                return relationships
        finally:
            self.connection_manager.release_connection(connection)

    def build_relationship_graph(self, schemas: List[str]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Build a complete relationship graph for all tables in the specified schemas.

        Args:
            schemas: List of schema names to analyze

        Returns:
            Dictionary mapping table identifiers to their relationships
        """
        query = """
                SELECT tc.constraint_name, \
                       tc.table_schema  AS source_schema, \
                       tc.table_name    AS source_table, \
                       kcu.column_name  AS source_column, \
                       ccu.table_schema AS target_schema, \
                       ccu.table_name   AS target_table, \
                       ccu.column_name  AS target_column
                FROM information_schema.table_constraints AS tc
                         JOIN information_schema.key_column_usage AS kcu
                              ON tc.constraint_name = kcu.constraint_name
                                  AND tc.table_schema = kcu.table_schema
                         JOIN information_schema.constraint_column_usage AS ccu
                              ON ccu.constraint_name = tc.constraint_name
                                  AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = ANY (%s)
                ORDER BY tc.table_schema, tc.table_name, tc.constraint_name; \
                """

        connection = self.connection_manager.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (schemas,))
                relationship_graph = {}

                for row in cursor.fetchall():
                    source_key = f"{row[1]}.{row[2]}"
                    target_key = f"{row[4]}.{row[5]}"

                    if source_key not in relationship_graph:
                        relationship_graph[source_key] = {
                            'outgoing': [],
                            'incoming': []
                        }

                    if target_key not in relationship_graph:
                        relationship_graph[target_key] = {
                            'outgoing': [],
                            'incoming': []
                        }

                    # Add outgoing relationship from source
                    relationship_graph[source_key]['outgoing'].append({
                        'constraint_name': row[0],
                        'source_column': row[3],
                        'target_schema': row[4],
                        'target_table': row[5],
                        'target_column': row[6]
                    })

                    # Add incoming relationship to target
                    relationship_graph[target_key]['incoming'].append({
                        'constraint_name': row[0],
                        'source_schema': row[1],
                        'source_table': row[2],
                        'source_column': row[3],
                        'target_column': row[6]
                    })

                logger.info(f"Built relationship graph for {len(relationship_graph)} tables")
                return relationship_graph
        finally:
            self.connection_manager.release_connection(connection)