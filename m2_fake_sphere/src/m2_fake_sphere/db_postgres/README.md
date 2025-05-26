# PostgreSQL Schema to JSON Converter

A Python tool that extracts PostgreSQL database schemas and converts them into nested JSON structures, preserving table relationships through foreign keys.

## Features

- **Schema Discovery**: Automatically discovers all schemas in your PostgreSQL database
- **Relationship Mapping**: Detects foreign key relationships and creates nested JSON structures
- **Circular Reference Handling**: Prevents infinite loops in self-referencing or circular relationships
- **Configurable Depth**: Control how deep the relationship nesting goes
- **Pretty Output**: Generate human-readable JSON with proper indentation
- **Configuration Persistence**: Save and reuse database connection settings

## Installation

1. Install Python 3.6 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the program interactively:
```bash
python main.py
```

The program will guide you through:
1. Database connection setup
2. Schema selection
3. Output configuration
4. Confirmation and execution

### Using a Configuration File

Create a configuration file (see `sample_config.json`) and run:
```bash
python main.py -c config.json
```

### Command Line Options

- `-c, --config`: Path to configuration file
- `-v, --verbose`: Enable verbose logging
- `--version`: Show version information

### Example

```bash
# Run with verbose logging
python main.py -v

# Use existing configuration
python main.py -c my_database_config.json
```

## Output Structure

The generated JSON follows this structure:

```json
{
  "schema_name": {
    "table_name": {
      "_table_info": {
        "schema": "schema_name",
        "table": "table_name",
        "primary_keys": ["id"]
      },
      "columns": {
        "column_name": {
          "data_type": "integer",
          "nullable": false,
          "is_primary_key": true
        }
      },
      "references": {
        "referenced_table_via_foreign_key": {
          "foreign_key": "user_id",
          "references_column": "id",
          "referenced_table": { /* nested structure */ }
        }
      },
      "referenced_by": {
        "child_table_via_foreign_key": {
          "foreign_key_column": "parent_id",
          "references_this_column": "id",
          "is_array": true,
          "items": { /* nested structure */ }
        }
      }
    }
  }
}
```

## Key Components

### 1. **database_connector.py**
Manages PostgreSQL connections with connection pooling for efficiency.

### 2. **schema_inspector.py**
Queries the database information schema to extract table and column metadata.

### 3. **relationship_mapper.py**
Detects foreign key relationships between tables to build the relationship graph.

### 4. **json_builder.py**
Constructs the nested JSON structure based on discovered relationships.

### 5. **config_manager.py**
Handles user input and configuration persistence.

### 6. **main.py**
Orchestrates the entire process from connection to JSON export.

## Configuration File Format

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "your_database",
    "user": "your_user",
    "password": ""  // Leave empty for security
  },
  "selected_schemas": ["public", "sales"],
  "output": {
    "file_path": "output.json",
    "pretty_print": true,
    "max_depth": 3
  }
}
```

## Notes

- Passwords are never saved to configuration files for security
- The tool handles circular references by limiting recursion depth
- Large databases may take time to process - use verbose mode to monitor progress
- The generated JSON preserves both forward (references) and reverse (referenced_by) relationships

## Troubleshooting

1. **Connection Issues**: Ensure PostgreSQL is running and credentials are correct
2. **Permission Errors**: User needs SELECT permission on information_schema
3. **Memory Issues**: For very large schemas, consider processing one schema at a time
4. **Circular References**: Adjust max_depth if you see too many circular reference markers

## License

This tool is provided as-is for database documentation and analysis purposes.