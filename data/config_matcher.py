import json
from enum import Enum, auto

from faker import Faker


class FakeDataGenerator:

    def __init__(self, number_records, current_record_number, config_file):
        """
        Initializes the Fake Data Generator
        """
        self.number_records = number_records
        self.config_file = config_file
        self.current_record_number = current_record_number
        self.config = self.load_config()
        self.fake = Faker()
        self.sequences = {}

    def load_config(self):
        """
        Loads the configuration file to memory
        """
        with open(self.config_file, 'r') as conf:
            return json.load(conf)

    def map_config(self):
        """
        Matches the configuration attributes to the Faker library functions
        """

        for attribute in self.config["attributes"]:
            col_name = attribute["columnName"]
            datatype = attribute["datatype"]
            desc = attribute["description"]
            bus_name = attribute["businessName"]
            bus_name = bus_name.replace(" ", "_").lower()
            print(bus_name)


if __name__ == '__main__':
    generator = FakeDataGenerator(2, 0, '../test/fake_csv/test_config.json')
    generator.map_config()
