
from cuid import CuidGenerator


def generator():

    # uniqueId = CUID().generate()
    uniqueId = CuidGenerator().cuid()
    return uniqueId



print(generator())