"""
Example Usage Script
This script demonstrates programmatic usage of the PostgreSQL Schema to JSON converter.
"""

from database_connector import DatabaseConnectionManager
from schema_inspector import SchemaInspector
from relationship_mapper import RelationshipMapper
from json_builder import JsonStructureBuilder


def example_basic_usage():
    """
    Example of basic usage without interactive prompts.
    """
    # Database configuration
    database_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'example_db',
        'user': 'postgres',
        'password': 'your_password'
    }

    # Initialize components
    connection_manager = DatabaseConnectionManager(database_config)
    schema_inspector = SchemaInspector(connection_manager)
    relationship_mapper = RelationshipMapper(connection_manager)
    json_builder = JsonStructureBuilder(schema_inspector, relationship_mapper)

    try:
        # Get all schemas
        schemas = schema_inspector.get_schemas()
        print(f"Found schemas: {schemas}")

        # Select specific schemas
        selected_schemas = ['public']  # or use all schemas

        # Build the complete structure
        database_structure = json_builder.build_schema_structure(selected_schemas)

        # Export to JSON
        json_builder.export_to_json(
            database_structure,
            'example_output.json',
            pretty_print=True
        )

        print("Export completed successfully!")

    finally:
        # Always close connections
        connection_manager.close_all_connections()


def example_single_table():
    """
    Example of extracting a single table structure.
    """
    # Database configuration
    database_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'example_db',
        'user': 'postgres',
        'password': 'your_password'
    }

    # Initialize components
    connection_manager = DatabaseConnectionManager(database_config)
    schema_inspector = SchemaInspector(connection_manager)
    relationship_mapper = RelationshipMapper(connection_manager)
    json_builder = JsonStructureBuilder(schema_inspector, relationship_mapper)

    try:
        # Get relationship graph for all schemas
        relationship_graph = relationship_mapper.build_relationship_graph(['public'])

        # Build structure for a single table
        table_structure = json_builder.build_table_structure(
            schema_name='public',
            table_name='users',  # Replace with your table name
            relationship_graph=relationship_graph,
            max_depth=2
        )

        # Export single table structure
        import json
        with open('single_table_output.json', 'w') as file:
            json.dump(table_structure, file, indent=2)

        print("Single table export completed!")

    finally:
        connection_manager.close_all_connections()


def example_custom_filtering():
    """
    Example with custom schema and table filtering.
    """
    # Database configuration
    database_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'example_db',
        'user': 'postgres',
        'password': 'your_password'
    }

    # Initialize components
    connection_manager = DatabaseConnectionManager(database_config)
    schema_inspector = SchemaInspector(connection_manager)
    relationship_mapper = RelationshipMapper(connection_manager)

    try:
        # Get all schemas
        all_schemas = schema_inspector.get_schemas()

        # Filter schemas (exclude system schemas)
        filtered_schemas = [s for s in all_schemas if not s.startswith('pg_')]

        # For each schema, get tables and filter
        for schema in filtered_schemas:
            tables = schema_inspector.get_tables_in_schema(schema)

            # Example: Only include tables that start with 'app_'
            app_tables = [t for t in tables if t.startswith('app_')]

            print(f"Schema: {schema}")
            print(f"  App tables: {app_tables}")

            # Get relationships for specific tables
            for table in app_tables:
                relationships = relationship_mapper.get_foreign_key_relationships(
                    schema,
                    table
                )
                print(f"    {table} has {len(relationships)} foreign keys")

    finally:
        connection_manager.close_all_connections()


if __name__ == "__main__":
    print("PostgreSQL Schema to JSON - Example Usage")
    print("========================================")

    # Uncomment the example you want to run:

    # example_basic_usage()
    # example_single_table()
    # example_custom_filtering()

    print("\nNote: Update the database configuration before running!")