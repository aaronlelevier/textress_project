import random
from string import digits


def salt(length=7):
    return "".join([random.choice(digits) for x in range(length)])
