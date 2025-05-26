"""
Configuration Manager
This module handles user input for database configuration and schema selection.
"""

import os
import getpass
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """
    Manages configuration for database connections and schema selection.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Optional path to a configuration file
        """
        self.config_file = config_file
        self.configuration: Dict[str, Any] = {}

    def load_configuration_from_file(self) -> bool:
        """
        Load configuration from a JSON file if it exists.

        Returns:
            True if the configuration was loaded successfully, False otherwise
        """
        if not self.config_file or not os.path.exists(self.config_file):
            return False

        try:
            with open(self.config_file, 'r') as file:
                self.configuration = json.load(file)
            logger.info(f"Configuration loaded from {self.config_file}")
            return True
        except Exception as error:
            logger.error(f"Failed to load configuration file: {error}")
            return False

    def save_configuration_to_file(self) -> None:
        """
        Save the current configuration to a JSON file.
        """
        if not self.config_file:
            return

        try:
            # Don't save password to file for security
            config_to_save = self.configuration.copy()
            if 'database' in config_to_save and 'password' in config_to_save['database']:
                config_to_save['database']['password'] = ""

            with open(self.config_file, 'w') as file:
                json.dump(config_to_save, file, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as error:
            logger.error(f"Failed to save configuration: {error}")

    def get_database_configuration(self) -> Dict[str, Any]:
        """
        Get database connection configuration from user input.

        Returns:
            Dictionary containing database connection parameters
        """
        print("\n=== PostgreSQL Database Configuration ===")

        # Check if we have existing configuration
        if 'database' in self.configuration:
            use_existing = input("Use existing database configuration? (y/n): ").lower()
            if use_existing == 'y':
                # Still need to get password if not stored
                if not self.configuration['database'].get('password'):
                    self.configuration['database']['password'] = getpass.getpass("Password: ")
                return self.configuration['database']

        # Get new configuration
        database_config = {
            'host': input("Host (default: localhost): ") or 'localhost',
            'port': int(input("Port (default: 5432): ") or 5432),
            'database': input("Database name: "),
            'user': input("Username: "),
            'password': getpass.getpass("Password: ")
        }

        self.configuration['database'] = database_config
        return database_config

    def select_schemas(self, available_schemas: List[str]) -> List[str]:
        """
        Allow user to select which schemas to process.

        Args:
            available_schemas: List of available schema names

        Returns:
            List of selected schema names
        """
        print("\n=== Schema Selection ===")
        print("Available schemas:")

        for index, schema in enumerate(available_schemas, 1):
            print(f"  {index}. {schema}")

        print("\nOptions:")
        print("  - Enter schema numbers separated by commas (e.g., 1,3,5)")
        print("  - Enter schema names separated by commas (e.g., public,sales)")
        print("  - Enter 'all' to select all schemas")
        print("  - Press Enter to select 'public' schema only")

        selection = input("\nYour selection: ").strip()

        if not selection:
            # Default to public schema
            return ['public'] if 'public' in available_schemas else []

        if selection.lower() == 'all':
            return available_schemas

        selected_schemas = []

        # Try to parse as numbers first
        try:
            indices = [int(num.strip()) - 1 for num in selection.split(',')]
            for index in indices:
                if 0 <= index < len(available_schemas):
                    selected_schemas.append(available_schemas[index])
        except ValueError:
            # Parse as schema names
            schema_names = [name.strip() for name in selection.split(',')]
            for schema_name in schema_names:
                if schema_name in available_schemas:
                    selected_schemas.append(schema_name)

        if not selected_schemas:
            logger.warning("No valid schemas selected")

        return selected_schemas

    def get_output_configuration(self) -> Dict[str, Any]:
        """
        Get output configuration from user input.

        Returns:
            Dictionary containing output configuration
        """
        print("\n=== Output Configuration ===")

        output_config = {
            'file_path': input("Output JSON file path (default: database_structure.json): ")
                         or 'database_structure.json',
            'pretty_print': input("Pretty print JSON? (y/n, default: y): ").lower() != 'n',
            'max_depth': int(input("Maximum relationship depth (default: 3): ") or 3)
        }

        self.configuration['output'] = output_config
        return output_config

    def confirm_configuration(self) -> bool:
        """
        Display configuration summary and get user confirmation.

        Returns:
            True if user confirms, False otherwise
        """
        print("\n=== Configuration Summary ===")
        print(f"Database: {self.configuration['database']['database']}")
        print(f"Host: {self.configuration['database']['host']}:{self.configuration['database']['port']}")
        print(f"User: {self.configuration['database']['user']}")
        print(f"Selected schemas: {', '.join(self.configuration.get('selected_schemas', []))}")
        print(f"Output file: {self.configuration['output']['file_path']}")
        print(f"Max relationship depth: {self.configuration['output']['max_depth']}")

        confirmation = input("\nProceed with this configuration? (y/n): ").lower()
        return confirmation == 'y'