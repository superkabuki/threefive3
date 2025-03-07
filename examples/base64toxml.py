#!/usr/bin/env python3
"""
base64toxml.py convert a SCTE-35 base64 encoded string to Xml,
and then convert the xml back to base64

"""

from threefive3 import Cue


if __name__ == "__main__":

    #  Base64 To Xml .
    b64 = "/DAWAAAAAAAAAP/wBQb+z26yLwAAXeqFJg=="
    cue = Cue(b64)  # initialize a Cue instance with the base64 string.
    exemel = cue.xml()  # call the Cue.xml() method
    print("\nbase64  -> xml\n")
    print(exemel)

    # Xml  to Base64.
    cue2 = Cue(exemel)  # initialize a Cue instance with the xml output from above..
    b64out = cue2.base64()  # call the Cue.base64() method
    print("xml -> base64\n\n")
    print(b64out)
