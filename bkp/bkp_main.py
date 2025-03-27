# fakeSphere/main.py
# pip install sqlalchemy psycopg2-binary pandas faker spacy
# python -m spacy download en_core_web_sm

from db_connector import DatabaseConnector
from schema_analyzer import SchemaAnalyzer
from data_generator import DataGenerator
from data_saver import DataSaver

class FakeSphere:
    def __init__(self, connection_string: str, database_name: str, context: str, github_repo: str = None):
        self.db_connector = DatabaseConnector(connection_string, database_name)
        self.schema_analyzer = SchemaAnalyzer(self.db_connector)
        self.data_generator = DataGenerator(self.db_connector, self.schema_analyzer, context)
        self.data_saver = DataSaver(self.db_connector)
        self.github_repo = github_repo

    def run(self, num_records: int = 100):
        self.schema_analyzer.analyze_structure()
        simulated_data = self.data_generator.generate_simulated_data(num_records)
        self.data_saver.save_to_database(simulated_data)
        return simulated_data

def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def get_connection_string():
    """Prompt user to build a PostgreSQL connection string."""
    print("\n=== Database Connection Setup ===")
    username = input("Enter database username: ").strip()
    password = input("Enter database password: ").strip()
    host = input("Enter database host (default: localhost): ").strip() or "localhost"
    port = input("Enter database port (default: 5432): ").strip() or "5432"
    return f"postgresql://{username}:{password}@{host}:{port}"

def get_context():
    """Prompt user to enter a context sentence."""
    print("\n=== Enter Database Context ===")
    print("Example: 'This database stores customer orders and product information.'")
    context = input("Enter a sentence describing the database: ").strip()
    return context

def terminal_menu():
    """Main terminal menu interface."""
    clear_screen()
    print("=== Welcome to Fake Sphere - Database Simulator ===")
    
    # Get connection details
    connection_string = get_connection_string()
    database_name = input("Enter database name: ").strip()
    
    # Get context
    context = get_context()
    
    # Get GitHub repo (optional)
    use_github = input("\nUse GitHub repository for schema? (y/n): ").strip().lower()
    github_repo = None
    if use_github == 'y':
        github_repo = input("Enter GitHub repository URL: ").strip()
    
    # Get number of records
    while True:
        try:
            num_records = input("\nEnter number of records to generate (default: 100): ").strip()
            num_records = int(num_records) if num_records else 100
            if num_records > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Confirm settings
    clear_screen()
    print("\n=== Configuration Summary ===")
    print(f"Connection String: {connection_string}/{database_name}")
    print(f"Context: {context}")
    print(f"GitHub Repository: {github_repo or 'Not specified'}")
    print(f"Number of Records: {num_records}")
    
    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Run simulation
    try:
        simulator = FakeSphere(connection_string, database_name, context, github_repo)
        simulated_data = simulator.run(num_records)
        
        print("\n=== Simulation Complete ===")
        for table, df in simulated_data.items():
            print(f"\nSample data for {table}:")
            print(df.head())
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

def bkp_main():
    while True:
        terminal_menu()
        again = input("\nRun again? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break

# if __name__ == "__main__":
#     bkp_main()