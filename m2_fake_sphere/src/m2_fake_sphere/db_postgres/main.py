"""
Main Program - PostgreSQL Schema to JSON Converter
This is the main entry point that orchestrates the database schema extraction process.
"""

import sys
import logging
import argparse
from typing import Optional

# Import all modules
from database_connector import DatabaseConnectionManager
from schema_inspector import SchemaInspector
from relationship_mapper import RelationshipMapper
from json_builder import JsonStructureBuilder
from config_manager import ConfigurationManager


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: Enable verbose logging if True
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('schema_to_json.log')
        ]
    )


def main(config_file: Optional[str] = None, verbose: bool = False) -> None:
    """
    Main execution function that coordinates the schema extraction process.

    Args:
        config_file: Optional path to configuration file
        verbose: Enable verbose logging
    """
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info("Starting PostgreSQL Schema to JSON Converter")

    try:
        # Initialize configuration manager
        config_manager = ConfigurationManager(config_file)

        # Load existing configuration if available
        config_manager.load_configuration_from_file()

        # Get database configuration
        database_config = config_manager.get_database_configuration()

        # Initialize database connection
        logger.info("Connecting to database...")
        connection_manager = DatabaseConnectionManager(database_config)

        # Initialize inspectors
        schema_inspector = SchemaInspector(connection_manager)
        relationship_mapper = RelationshipMapper(connection_manager)

        # Get available schemas
        available_schemas = schema_inspector.get_schemas()

        if not available_schemas:
            logger.error("No schemas found in the database")
            return

        # Let user select schemas
        selected_schemas = config_manager.select_schemas(available_schemas)

        if not selected_schemas:
            logger.error("No schemas selected")
            return

        config_manager.configuration['selected_schemas'] = selected_schemas

        # Get output configuration
        output_config = config_manager.get_output_configuration()

        # Confirm configuration
        if not config_manager.confirm_configuration():
            logger.info("Operation cancelled by user")
            return

        # Save configuration for future use
        config_manager.save_configuration_to_file()

        # Initialize JSON builder
        json_builder = JsonStructureBuilder(schema_inspector, relationship_mapper)

        # Build the database structure
        logger.info("Building database structure...")
        database_structure = json_builder.build_schema_structure(selected_schemas)

        # Export to JSON
        json_builder.export_to_json(
            database_structure,
            output_config['file_path'],
            output_config['pretty_print']
        )

        logger.info(f"Successfully exported database structure to {output_config['file_path']}")
        print(f"\n✅ Database structure exported to: {output_config['file_path']}")

    except Exception as error:
        logger.error(f"An error occurred: {error}", exc_info=True)
        print(f"\n❌ Error: {error}")
        sys.exit(1)

    finally:
        # Clean up connections
        if 'connection_manager' in locals():
            connection_manager.close_all_connections()
            logger.info("Database connections closed")


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='PostgreSQL Schema to JSON Converter - Extract database schema with relationships'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file (JSON format)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser.parse_args()


if __name__ == "__main__":
    """
    Entry point when running as a script.
    """
    args = parse_arguments()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          PostgreSQL Schema to JSON Converter              ║
    ║                    Version 1.0.0                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    main(config_file=args.config, verbose=args.verbose)