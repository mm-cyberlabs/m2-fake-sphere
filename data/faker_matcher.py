import json

from faker import Faker
from rapidfuzz import process
from rapidfuzz.fuzz import ratio

from data.datatype_enum import Datatype

fake = Faker()


def _extract_faker_callables():
    """
    _extract_faker_callables() -> [] array of faker methods.

    The function will extract all the callable functions that do not start with '_' or 'seed'. All the callable
    functions are later used to do a fuzzy match with the business name attributes coming from the configuration
    file.
    """
    faker_methods = []
    for attr in dir(fake):
        # Avoid non-callable functions or internal Faker functions.
        if attr.startswith('_') or attr == 'seed':
            continue

        try:
            candidate = getattr(fake, attr)
        except TypeError:
            continue

        if callable(candidate):
            faker_methods.append(attr)
    return faker_methods


class FakerDataMatcher:
    """
    class to match business attribute names with Faker library callables.

    This class takes a business name (usually coming from a configuration file)
    and a data type, and attempts to find the best matching Faker method for generating
    synthetic data. For string data types, it uses fuzzy matching to compare the normalized
    business name (lowercase with underscores) against the list of available Faker methods.
    For non-string data types, no matching is performed (returns "NA").

    Attributes:
        - bus_name (str): The business name to be matched.
        - datatype (str): The data type of the attribute (e.g., STRING, NUMBER).

    Methods:
        - match(*dem_objs):
            A class method that processes one or more FakerDataMatcher objects, performs fuzzy matching
            for string attributes using RapidFuzz, and returns a dictionary mapping normalized business
            names to their best matches or "NA" if no match is applicable.
    """

    def __init__(self, business_name, datatype):
        self.bus_name = business_name
        self.datatype = datatype

    def match(*dem_objs):
        faker_methods = _extract_faker_callables()
        best_matches = {}
        for dem_obj in dem_objs:

            bus_name = dem_obj.bus_name.lower().replace(" ", "_")
            datatype = dem_obj.datatype.upper()

            if datatype == Datatype.STRING.name:

                if hasattr(fake, bus_name):
                    best_matches[bus_name] = bus_name

                best_matches[bus_name] = process.extract(bus_name, faker_methods, scorer=ratio, score_cutoff=55.0)

            else:
                best_matches[bus_name] = "NA"
        print(f"Best Matches: {json.dumps(best_matches)}")
        return best_matches


if __name__ == '__main__':
    # TODO: ERASE, for testing purposes only
    object_list = []
    with open('../test/fake_csv/test_config.json', 'r') as file:
        config = json.load(file)
    for entry in config["attributes"]:
        obj = FakerDataMatcher(entry["businessName"], entry["datatype"])
        object_list.append(obj)
        fake.first_name() + fake.last_name()

    FakerDataMatcher.match(*object_list)
