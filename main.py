# fakeSphere/main.py

import os
import logging

from config.logging_config import LoggerConfig

"""
    Clears the terminal screen.
"""
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


"""
    Displays the Fake Sphere logo.
"""
def display_logo():
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.txt')
    if os.path.exists(logo_path):
        with open(logo_path, 'r') as file:
            print(file.read())

"""
    Displays the main menu options and returns the user's choice.
"""
def display_menu():
    print("\n=== Welcome to Fake Sphere - A Simulation in the Matrix ===")
    print("\t 1. Generate Fake Data in a flat file [.csv]")
    print("\t 2. Generate Fake Data and insert to the database [SQL DB]")
    print("\t 3. API calls to simulate calls [REST API]")
    print("\t 4. Exit")
    choice = input("Enter your choice: ")
    return choice


def main():
    clear_screen()
    display_logo()
    choice = display_menu()
    log.info(f"Your choice is: {choice}")


if __name__ == "__main__":
    LoggerConfig.setup_logging()  # Setup logging using our config class
    
    log = logging.getLogger(__name__)  # Get a logger for this module
    log.info("Logging is configured!")
    main()


