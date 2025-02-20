"""
stuff.py functions and such common to threefive3.
"""

from sys import stderr


def print2(gonzo=b""):
    """
    print2 prints to 2 aka stderr.
    """
    print(gonzo, file=stderr, flush=True)


def atoif(value):
    """
    atoif converts ascii to (int|float)
    """
    if isinstance(value, str):
        value= value.strip()
        value = value.replace(',','')
        if '.' in value:
            value = float(value)
        elif  value.isdigit():
            value = int(value)
    return value
