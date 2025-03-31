from enum import Enum, auto


class Datatype(Enum):
    """
    Contains all the possible datatypes that Fake Sphere can handle.
    """
    SEQUENCE = auto()
    LOOKUP = auto()
    STRING = auto()
    NUMBER = auto()
