"""
crc.py  crc32 function for encoding.
"""

from .words import zero, one, eight, twentyfour, thirtytwo, twofiftyfive, twofiftysix

POLY = 0x104C11DB7
INIT_VALUE = 0xFFFFFFFF


def _bytecrc(crc, poly):
    mask = one << (thirtytwo - one)
    i = eight
    while i:
        crc = (crc << one, crc << one ^ poly)[crc & mask != zero]
        i -= one
    return crc & INIT_VALUE


def _mk_table():
    mask = (one << thirtytwo) - one
    poly = POLY & mask
    return [_bytecrc((i << twentyfour), poly) for i in range(twofiftysix)]


def crc32(data):
    """
    generate a 32 bit crc
    """

    table = _mk_table()
    crc = INIT_VALUE
    for bite in data:
        crc = table[bite ^ ((crc >> twentyfour) & twofiftyfive)] ^ (
            (crc << eight) & (INIT_VALUE - twofiftyfive)
        )
    return crc


def crc32hex(data):
    """
    crc32hex crc32 returned as hex
    """
    return hex(crc32(data))
