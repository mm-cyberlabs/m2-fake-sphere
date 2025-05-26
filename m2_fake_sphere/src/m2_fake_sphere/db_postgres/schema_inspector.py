"""
JSON Structure Builder
This module builds nested JSON structures representing database schemas with relationships.
"""

import json
from typing import Dict, List, Any, Set, Optional
import logging

logger = logging.getLogger(__name__)


def export_to_json(structure: Dict[str, Any], output_file: str,
                   pretty_print: bool = True) -> None:
    """
    Export the structure to a JSON file.

    Args:
        structure: The database structure dictionary
        output_file: Path to the output JSON file
        pretty_print: Whether to format the JSON with indentation
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            if pretty_print:
                json.dump(structure, json_file, indent=2, ensure_ascii=False)
            else:
                json.dump(structure, json_file, ensure_ascii=False)

        logger.info(f"Successfully exported structure to {output_file}")
    except Exception as error:
        logger.error(f"Failed to export JSON: {error}")
        raise


class JsonStructureBuilder:
    """
    Builds nested JSON structures representing database schemas and their relationships.
    """

    def __init__(self, schema_inspector, relationship_mapper):
        """
        Initialize the JSON structure builder.

        Args:
            schema_inspector: SchemaInspector instance
            relationship_mapper: RelationshipMapper instance
        """
        self.schema_inspector = schema_inspector
        self.relationship_mapper = relationship_mapper
        self.processed_tables: Set[str] = set()

    def build_table_structure(self, schema_name: str, table_name: str,
                              relationship_graph: Dict[str, Dict[str, List[Dict[str, Any]]]],
                              depth: int = 0, max_depth: int = 3) -> Dict[str, Any]:
        """
        Build the JSON structure for a single table including its relationships.

        Args:
            schema_name: Name of the schema
            table_name: Name of the table
            relationship_graph: Complete relationship graph
            depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent infinite loops

        Returns:
            Dictionary representing the table structure
        """
        table_key = f"{schema_name}.{table_name}"

        # Prevent infinite recursion and circular references
        if depth >= max_depth or table_key in self.processed_tables:
            return {
                "_reference": f"{schema_name}.{table_name}",
                "_circular_reference": True
            }

        self.processed_tables.add(table_key)

        # Get table columns
        columns = self.schema_inspector.get_column_details(schema_name, table_name)
        primary_keys = self.schema_inspector.get_primary_keys(schema_name, table_name)

        # Build column structure
        column_structure = {}
        for column in columns:
            column_info = {
                "data_type": column['data_type'],
                "nullable": column['is_nullable'],
                "is_primary_key": column['column_name'] in primary_keys
            }

            # Add additional details if present
            if column['max_length']:
                column_info['max_length'] = column['max_length']
            if column['default_value']:
                column_info['default'] = column['default_value']

            column_structure[column['column_name']] = column_info

        # Build table structure
        table_structure = {
            "_table_info": {
                "schema": schema_name,
                "table": table_name,
                "primary_keys": primary_keys
            },
            "columns": column_structure
        }

        # Add relationships if they exist
        if table_key in relationship_graph:
            relationships = relationship_graph[table_key]

            # Add outgoing relationships (this table references other tables)
            if relationships['outgoing']:
                table_structure['references'] = {}
                for rel in relationships['outgoing']:
                    ref_key = f"{rel['target_schema']}.{rel['target_table']}"
                    ref_name = f"{rel['target_table']}_via_{rel['source_column']}"

                    # Recursively build referenced table structure
                    referenced_structure = self.build_table_structure(
                        rel['target_schema'],
                        rel['target_table'],
                        relationship_graph,
                        depth + 1,
                        max_depth
                    )

                    table_structure['references'][ref_name] = {
                        "foreign_key": rel['source_column'],
                        "references_column": rel['target_column'],
                        "referenced_table": referenced_structure
                    }

            # Add incoming relationships (other tables reference this table)
            if relationships['incoming']:
                table_structure['referenced_by'] = {}
                for rel in relationships['incoming']:
                    ref_key = f"{rel['source_schema']}.{rel['source_table']}"
                    ref_name = f"{rel['source_table']}_via_{rel['source_column']}"

                    # For incoming relationships, we create an array structure
                    # since multiple records can reference this table
                    if ref_name not in table_structure['referenced_by']:
                        table_structure['referenced_by'][ref_name] = {
                            "foreign_key_column": rel['source_column'],
                            "references_this_column": rel['target_column'],
                            "is_array": True,
                            "items": self.build_table_structure(
                                rel['source_schema'],
                                rel['source_table'],
                                relationship_graph,
                                depth + 1,
                                max_depth
                            )
                        }

        # Remove from processed tables when returning
        self.processed_tables.remove(table_key)

        return table_structure

    def build_schema_structure(self, schemas: List[str]) -> Dict[str, Any]:
        """
        Build the complete JSON structure for all specified schemas.

        Args:
            schemas: List of schema names to process

        Returns:
            Dictionary representing the complete database structure
        """
        # Build a relationship graph first
        relationship_graph = self.relationship_mapper.build_relationship_graph(schemas)

        # Build the complete structure
        database_structure = {}

        for schema_name in schemas:
            logger.info(f"Processing schema: {schema_name}")
            schema_structure = {}

            # Get all tables in the schema
            tables = self.schema_inspector.get_tables_in_schema(schema_name)

            for table_name in tables:
                logger.debug(f"Processing table: {schema_name}.{table_name}")
                self.processed_tables.clear()  # Clear for each table

                table_structure = self.build_table_structure(
                    schema_name,
                    table_name,
                    relationship_graph
                )

                schema_structure[table_name] = table_structure

            database_structure[schema_name] = schema_structure

        return database_structure

