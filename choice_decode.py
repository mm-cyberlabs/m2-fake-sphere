# fakeSphere/choice_decode.py

import logging

def handle_choice(choice):
    """
    Processes the user input and executes the corresponding logic.
    :param choice: A string representing the menu option chosen by the user.
    """
    if choice == '1':
        # Generate Fake Data in a flat file [.csv]
        print("Generating fake CSV data...")
        # Add your CSV generation logic here
    elif choice == '2':
        # Generate Fake Data and insert into the database [SQL DB]
        print("Generating fake data for SQL DB...")
        # Add your SQL DB insertion logic here
    elif choice == '3':
        # API calls to simulate REST API interactions
        print("Simulating API calls...")
        # Add your API simulation logic here
    elif choice == '4':
        # Exit the application
        print("Exiting application...")
        exit()
    else:
        # Handle invalid input
        print("Invalid choice. Please try again.")

def handle_choice1():
    log = logging.getLogger()
    log.info("Choice 1 was chosen by the user.")

    