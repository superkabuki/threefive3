"""
sixfix.py
"""

import io
import sys
from .crc import crc32
from .bitn import NBin
from .stuff import red
from .stream import Stream

fixme = []


def passed(cue):
    """
    passed a no-op function
    """
    global fixme
    fixme.append(int(cue.packet_data.pid, base=16))
    return cue


class PreFix(Stream):
    """
    PreFix is used to gather 06 Bin data pids with SCTE-35.
    """

    def decode(self, func=passed):
        super().decode(func=passed)
        global fixme
        fixme = list(set(fixme))
        if fixme:
            print("fixing these pids", fixme)
        return fixme


class SixFix(Stream):
    """
    SixFix class
    fixes bin data streams with SCTE-35 to 0x86 SCTE-35 streams
    """

    CUEI_DESCRIPTOR = b"\x05\x04CUEI"

    def __init__(self, tsdata=None):
        super().__init__(tsdata)
        self.pmt_pays = {}
        self.pid_prog = {}
        self.con_pids = set()
        self.out_file = "sixfixed-" + tsdata.rsplit("/")[-1]
        self.in_file = sys.stdin.buffer

    def _parse_by_pid(self, pkt, pid):
        if pid in self.pids.tables:
            self._parse_tables(pkt, pid)
        if pid in self.pids.pmt:
            prgm = self.pid2prgm(pid)
            if prgm in self.pmt_pays:
                pkt = pkt[:4] + self.pmt_pays[prgm]
        return pkt

    def _parse_pkts(self, out_file):
        active = io.BytesIO()
        pkt_count = 0
        chunk_size = 2048
        for pkt in self.iter_pkts():
            pid = self._parse_pid(pkt[1], pkt[2])
            pkt = self._parse_by_pid(pkt, pid)
            active.write(pkt)
            pkt_count = (pkt_count + 1) % chunk_size
            if not pkt_count:
                out_file.write(active.getbuffer())
                active = io.BytesIO()

    def convert_pids(self):
        """
        convert_pids
        changes the stream type to 0x86 and replaces
        the existing PMT as it writes packets to the outfile
        """
        # if isinstance(self.out_file, str):
        #    self.out_file = open(self.out_file, "wb")
        with open(self.out_file, "wb") as out_file:
            self._parse_pkts(out_file)

    def _regen_pmt(
        self, prgm, n_seclen, pcr_pid, n_proginfolen, n_info_bites, n_streams
    ):
        nbin = NBin()
        nbin.add_int(2, 8)  # 0x02
        nbin.add_int(1, 1)  # section Syntax indicator
        nbin.add_int(0, 1)  # 0
        nbin.add_int(3, 2)  # reserved
        nbin.add_int(n_seclen, 12)  # section length
        nbin.add_int(prgm, 16)  # program number
        nbin.add_int(3, 2)  # reserved
        nbin.add_int(0, 5)  # version
        nbin.add_int(1, 1)  # current_next_indicator
        nbin.add_int(0, 8)  # section number
        nbin.add_int(0, 8)  # last section number
        nbin.add_int(7, 3)  # res
        nbin.add_int(pcr_pid, 13)
        nbin.add_int(15, 4)  # res
        nbin.add_int(n_proginfolen, 12)
        nbin.add_bites(n_info_bites)
        nbin.add_bites(n_streams)
        a_crc = crc32(nbin.bites)
        nbin.add_int(a_crc, 32)
        pointer_field = b"\x00"
        n_payload = pointer_field + nbin.bites
        pad = 184 - len(n_payload)
        if pad > 0:
            n_payload = n_payload + (b"\xff" * pad)
        self.pmt_pays[prgm] = n_payload

    def _chk_payload(self, pay, pid):
        pay = self._chk_partial(pay, pid, self._PMT_TID)
        if not pay:
            return False
        return pay

    def _parse_pmt(self, pay, pid):
        """
        parse program maps for streams
        """
        pay = self._chk_payload(pay, pid)
        if pay:
            seclen = self._parse_length(pay[1], pay[2])
            n_seclen = seclen + 6
            if self._section_incomplete(pay, pid, seclen):
                return False
        program_number = self._parse_program(pay[3], pay[4])
        pcr_pid = self._parse_pid(pay[8], pay[9])
        self.pids.pcr.add(pcr_pid)
        self.maps.pid_prgm[pcr_pid] = program_number
        self.maps.pid_prgm[pid] = program_number
        proginfolen = self._parse_length(pay[10], pay[11])
        idx = 12
        n_proginfolen = proginfolen + len(self.CUEI_DESCRIPTOR)
        end = idx + proginfolen
        info_bites = pay[idx:end]
        n_info_bites = info_bites + self.CUEI_DESCRIPTOR
        while idx < end:
            # d_type = pay[idx]
            idx += 1
            d_len = pay[idx]
            idx += 1
            # d_bytes = pay[idx - 2 : idx + d_len]
            idx += d_len
        si_len = seclen - 9
        si_len -= proginfolen
        n_streams = self._parse_program_streams(si_len, pay, idx, program_number)
        self._regen_pmt(
            program_number, n_seclen, pcr_pid, n_proginfolen, n_info_bites, n_streams
        )
        return True

    def _parse_program_streams(self, si_len, pay, idx, program_number):
        """
        parse the elementary streams
        from a program
        """
        chunk_size = 5
        end_idx = (idx + si_len) - 4
        start = idx
        while idx < end_idx:
            pay, stream_type, pid, ei_len = self._parse_stream_type(pay, idx)
            idx += chunk_size
            idx += ei_len
            self.maps.pid_prgm[pid] = program_number
            self._set_scte35_pids(pid, stream_type)
        streams = pay[start:end_idx]
        return streams

    def _parse_stream_type(self, pay, idx):
        """
        extract stream pid and type
        """
        npay = pay
        stream_type = pay[idx]
        el_pid = self._parse_pid(pay[idx + 1], pay[idx + 2])
        if el_pid in self.con_pids:
            if stream_type == 6:
                npay = pay[:idx] + b"\x86" + pay[idx + 1 :]
        ei_len = self._parse_length(pay[idx + 3], pay[idx + 4])
        return npay, stream_type, el_pid, ei_len


def sixfix(arg):
    """
    sixfix converts 0x6 bin data mpegts streams
    that contain SCTE-35 data to stream type 0x86
    """
    s1 = PreFix(arg)
    sixed = s1.decode(func=passed)
    global fixme
    fixme = []
    if not sixed:
        red("No bin data SCTE-35 streams were found.")
        return
    s2 = SixFix(arg)
    s2.con_pids = sixed
    s2.convert_pids()
    red(f'Wrote: sixfixed-{arg.rsplit("/")[-1]}\n')
    return


if __name__ == "__main__":
    sixfix(sys.argv[1])
