import random


class SequenceDataGenerator:
    """
    Generates the fake data.
    """

    def __init__(self):
        self.sequence_surrogate_key_generator = {}
        self.sequence_lookup_reference_selector = {}

    def sequence_surrogate_key_generator(self, col_name):
        """
        This will create a sequence if the datatype is a sequence for the fields
        that are assigned as a sequence.
        """
        if col_name not in self.sequence_surrogate_key_generator:
            self.sequence_surrogate_key_generator[col_name] = 0
        self.sequence_surrogate_key_generator[col_name] += 1
        print(f"{col_name} = seq: {self.sequence_surrogate_key_generator[col_name]}")

    def sequence_lookup_reference_selector(self, table_name):
        """
        It will select a random existing sequence of a table that is already created. If the table is not existing
        yet in memory, then it will create the data and populate the sequence.
        NOTE: This is mainly used for SQL data population.
        """
        if table_name not in self.sequence_lookup_reference_selector[table_name]:
            # TODO: add logic to look up for table name and populate the static data.
            return 0
        else:
            # From an existing sequence for the input table, it will select a random sequence.
            return random.randint(1, self.sequence_lookup_reference_selector[table_name])
