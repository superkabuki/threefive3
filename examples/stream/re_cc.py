#!/usr/bin/env python3

"""
re_cc.py is an example of subclassing the threefive3.Stream class

re_cc.py  parses an MPEGTS stream  and recalculates
the continuity counter for each packet.

Input can be a local file, http(s), UDP, Multicast or stdin
Output is written to stdout.

Example usage:

python3 re_cc.py video.ts > recced.ts

cat video.ts | python3 re_cc.py |  your_app

python3 re_cc.py https://futzu.com/xaa.ts > output.ts


"""


import sys
from functools import partial
from threefive3 import Stream, blue



class ResetCC(Stream):
    def re_cc(self, proxy=True,):
        """
        re_cc resets the continuity counters.
        MPEGTS packets are written to stdout for piping.
        """
  
        outfile = sys.stdout.buffer  # write to stdout
        num_pkts = 1300   # how many packets to read at once
        for chunk in self.iter_pkts(num_pkts=num_pkts):  # chunk will have 1300 pkts
            chunky =bytearray(chunk) # Convert to a byte array to make it easier to rewrite packets.
            chunks = [
                self._set_cc(chunky[i : i + self._PACKET_SIZE])
                for i in range(0, len(chunky), self._PACKET_SIZE)
            ] # split chunky into packets and set cc 
            outfile.write(b"".join(chunks)) 

    def _set_cc(self, pkt):
        pid = self._parse_pid(pkt[1], pkt[2])
        if pid == 0x1FFF:
            return pkt
        new_cc = 0
        if pid in self.maps.pid_cc:
            last_cc = self.maps.pid_cc[pid]
            new_cc = (last_cc + 1) % 16  # continuity counters roll over at 16
        pkt[3] &= 0xF0 # clobber old cc from third byte in the packet
        pkt[3] += new_cc # set new cc value in third byte

        self.maps.pid_cc[pid] = new_cc  # track cc by each pid
        return pkt


if __name__ == "__main__":
    infile= sys.stdin.buffer
    if len(sys.argv) > 1:
        infile= sys.argv[1]  # if a URI is provided, use it. 
    resetter = ResetCC(infile)
    resetter.re_cc()
