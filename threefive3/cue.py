"""
scte35.Cue Class
"""

from base64 import b64decode, b64encode
import json
from .spare import print2
from .bitn import NBin
from .base import SCTE35Base
from .section import SpliceInfoSection
from .commands import command_map, SpliceCommand
from .descriptors import splice_descriptor, descriptor_map
from .crc import crc32
from .xml import Node
from .segmentation import table22
from .x2c import xml2cue


class Cue(SCTE35Base):
    """
    The threefive3.Cue class handles parsing
    SCTE 35 message strings.
    Example usage:

    >>>> import threefive3
    >>>> Base64 = "/DAvAAAAAAAA///wBQb+dGKQoAAZAhdDVUVJSAAAjn+fCAgAAAAALKChijUCAKnMZ1g="
    >>>> cue = threefive3.Cue(Base64)
    >>>> cue.show()

    * A cue instance can be initialized with
     Base64, Bytes, Hex, Int, Json, Xml, or Xml+binary data.

    * Instance variables can be accessed via dot notation.

    >>>> cue.command
    {'command_length': 5, 'name': 'Time Signal', 'time_specified_flag': True,
    'pts_time': 21695.740089}

    >>>> cue.command.pts_time
    21695.740089


    """

    def __init__(self, data=None, packet_data=None):
        """
        data may be packet bites or encoded string
        packet_data is a instance passed from a Stream instance
        """
        self.errors=[]
        self.command = None
        self.descriptors = []
        self.info_section = SpliceInfoSection()
        self.bites = None
        if data:
            self.bites = self._mk_bits(data)
            self.decode()
        self.packet_data = packet_data
        self.dash_data = None
        self.decode()

    def __repr__(self):
        return str(self.__dict__)

    def errs(self):
        """
        errs  show encoding errors.
        """         
        e= {"cue.errors": self.errors}
        if self.info_section:
           e["info_section_errors"] = self.info_section.has("errors")
        if isinstance(self.command,  SpliceCommand):
            e["command_errors"]= self.command.errors
        e["descriptor_errors"] = [d.errors for d in self.descriptors]
        return e
    
    def decode(self):
        """
        Cue.decode() parses for SCTE35 data

        * decode doesn't need to be called directly
           unless you initialize a Cue without data.
        """
        bites = self.bites
        self.descriptors = []
        while bites:
            bites = self.mk_info_section(bites)
            bites = self._set_splice_command(bites)
            bites = self._mk_descriptors(bites)
            if bites:
                crc = hex(int.from_bytes(bites[0:4], byteorder="big"))
                self.info_section.crc = crc
                return True
        return False

    def _descriptor_loop(self, loop_bites):
        """
        Cue._descriptor_loop parses all splice descriptors
        """
        tag_n_len = 2
        while len(loop_bites) > tag_n_len:
            spliced = splice_descriptor(loop_bites)
            if not spliced:
                return
            sd_size = tag_n_len + spliced.descriptor_length
            loop_bites = loop_bites[sd_size:]
            del spliced.bites
            self.descriptors.append(spliced)

    def _get_dash_data(self, scte35_dict):
        if self.dash_data:
            scte35_dict["dash_data"] = self.dash_data
        return scte35_dict

    def _get_packet_data(self, scte35_dict):
        if self.packet_data:
            scte35_dict["packet_data"] = self.packet_data.get()
        return scte35_dict

    def get(self):
        """
        Cue.get returns the SCTE-35 Cue
        data as a dict of dicts.
        """
        if self.command and self.info_section:
            scte35_data = {
                "info_section": self.info_section.get(),
                "command": self.command.get(),
                "descriptors": self.get_descriptors(),
            }
            scte35_data = self._get_dash_data(scte35_data)
            scte35_data = self._get_packet_data(scte35_data)
            return scte35_data
        self.errors.append("command or info section not found")
        return False

    def get_descriptors(self):
        """
        Cue.get_descriptors returns a list of
        SCTE 35 splice descriptors as dicts.
        """
        return [d.get() for d in self.descriptors]

    def bytes(self):
        """
        get_bytes returns Cue.bites
        """
        return self.bites

    def fix_bad_b64(self,data):
        """
        fix_bad_b64 fixes bad padding on Base64
        """
        if len(data) %4!=0:
            self.errors.append('fixed bad base64 length ')
        while len(data) % 4 != 0:
            data = data + "="
        return data

    def _int_bits(self, data):
        """
        _int_bits convert a SCTE-35 Cue from integer to bytes.
        """
        length = data.bit_length() >> 3
        bites = int.to_bytes(data, length, byteorder="big")
        return bites

    def _hex_bits(self, data):
        """
        _hex_bits convert a SCTE-35 Cue from hex to bytes.
        """
        try:
            i = int(data, 16)
            i_len = i.bit_length() >> 3
            bites = int.to_bytes(i, i_len, byteorder="big")
            return bites
        except (LookupError, TypeError, ValueError):
            if data[:2].lower() == "0x":
                data = data[2:]
            if data[:2].lower() == "fc":
                return bytes.fromhex(data)
        return b""

    def _b64_bits(self, data):
        """
        _b64_bits decode base64 to bytes
        """
        try:
            return b64decode(self.fix_bad_b64(data))
        except (LookupError, TypeError, ValueError):
            return data

    def _str_bits(self, data):
        try:
            self.load(data)
            return self.bites
        except (LookupError, TypeError, ValueError):
            hex_bits = self._hex_bits(data)
            if hex_bits:
                return hex_bits
        return self._b64_bits(data)

    def _mk_bits(self, data):
        """
        cue._mk_bits Converts
        Hex and Base64 strings into bytes.
        """
        bites = data
        if isinstance(data, dict):
            self.load(data)
            return self.bites
        if isinstance(data, Node):
            self.load(data.mk())
            return self.bites
        if isinstance(data, bytes):
            bites = self.idxsplit(data, b"\xfc")
        if isinstance(data, int):
            bites = self._int_bits(data)
        if isinstance(data, str):
            bites = self._str_bits(data)
        self.bites = bites
        self.decode()
        return bites

    def _mk_descriptors(self, bites):
        """
        Cue._mk_descriptors parses
        Cue.info_section.descriptor_loop_length,
        then call Cue._descriptor_loop
        """
        ##        if len(bites) < 2:
        ##            return False
        while bites:
            dll = (bites[0] << 8) | bites[1]
            self.info_section.descriptor_loop_length = dll
            bites = bites[2:]
            self._descriptor_loop(bites[:dll])
            return bites[dll:]

    def mk_info_section(self, bites):
        """
        Cue.mk_info_section parses the
        Splice Info Section
        of a SCTE35 cue.
        """
        info_size = 14
        info_bites = bites[:info_size]
        self.info_section.decode(info_bites)
        return bites[info_size:]

    def _set_splice_command(self, bites):
        """
        Cue._set_splice_command parses
        the command section of a SCTE35 cue.
        """
        sct = self.info_section.splice_command_type
        if sct not in command_map:
            self.errors.append(f"Splice Command type {sct} not recognized") 
            return False
        iscl = self.info_section.splice_command_length
        cmd_bites = bites[:iscl]
        self.command = command_map[sct](cmd_bites)
        self.command.command_length = iscl
        self.command.decode()
        del self.command.bites
        return bites[iscl:]

    # encode related

    def _assemble(self):
        for d in self.descriptors:
            d.errors=[]
        dscptr_bites = self._unloop_descriptors()
        dll = len(dscptr_bites)
        self.info_section.descriptor_loop_length = dll
        self.info_section.errors=[]
        self.command.errors=[]
        cmd_bites = self.command.encode()
        cmdl = self.command.command_length = len(cmd_bites)
        self.info_section.splice_command_length = cmdl
        self.info_section.splice_command_type = self.command.command_type
        # 11 bytes for info section + command + 2 descriptor loop length
        # + descriptor loop + 4 for crc
        self.info_section.section_length = 11 + cmdl + 2 + dll + 4
        self.bites = self.info_section.encode()
        self.bites += cmd_bites
        self.bites += int.to_bytes(
            self.info_section.descriptor_loop_length, 2, byteorder="big"
        )
        self.bites += dscptr_bites

    def base64(self):
        """
        base64 Cue.base64() converts SCTE35 data
        to a base64 encoded string.
        """
        if self.command:
            self._assemble()
            self._encode_crc()
            return b64encode(self.bites).decode()
        self._no_cmd()
        return False

    def encode(self):
        """
        encode is an alias for base64
        """
        return self.base64()

    def int(self):
        """
        int returns self.bites as an int.
        """
        self.encode()
        return int.from_bytes(self.bites, byteorder="big")

    def hex(self):
        """
        hex returns self.bites as
        a hex string
        """
        return hex(self.int())

    def _encode_crc(self):
        """
        _encode_crc encode crc32
        """
        crc_int = crc32(self.bites)
        self.info_section.crc = hex(crc_int)
        self.bites += int.to_bytes(crc_int, 4, byteorder="big")

    def _unloop_descriptors(self):
        """
        _unloop_descriptors
        for each descriptor in self.descriptors
        encode descriptor tag, descriptor length,
        and the descriptor into all_bites.bites
        """
        all_bites = NBin()
        dbite_chunks = [dsptr.encode() for dsptr in self.descriptors]
        for chunk, dsptr in zip(dbite_chunks, self.descriptors):
            dsptr.descriptor_length = len(chunk)
            all_bites.add_int(dsptr.tag, 8)
            all_bites.add_int(dsptr.descriptor_length, 8)
            all_bites.add_bites(chunk)
        return all_bites.bites

    def _load_info_section(self, gonzo):
        """
        load_info_section loads data for Cue.info_section
        isec should be a dict.
        if 'splice_command_type' is included,
        an empty command instance will be created for Cue.command
        """
        if "info_section" in gonzo:
            self.info_section.load(gonzo["info_section"])

    def _load_command(self, gonzo):
        """
        load_command loads data for Cue.command
        cmd should be a dict.
        if 'command_type' is included,
        the command instance will be created.
        """
        if "command" not in gonzo:
            self._no_cmd()
            return False
        cmd = gonzo["command"]
        if "command_type" in cmd:
            self.command = command_map[cmd["command_type"]]()
            self.command.load(cmd)

    def _load_descriptors(self, dlist):
        """
        Load_descriptors loads descriptor data.
        dlist is a list of dicts
        if 'tag' is included in each dict,
        a descriptor instance will be created.
        """
        ##        if not isinstance(dlist, list):
        ##            raise Exception("\033[7mdescriptors should be a list\033[27m")
        for dstuff in dlist:
            dscptr = descriptor_map[dstuff["tag"]]()
            dscptr.load(dstuff)
            self.descriptors.append(dscptr)

    def _no_cmd(self):
        """
        _no_cmd raises an exception if no splice command.
        """
        self.errors.append("A splice command is required")
      #  raise Exception("\033[7mA splice command is required\033[27m")

    def load(self, gonzo):
        """
        Cue.load loads SCTE35 data for encoding.
        gonzo is a dict or json
        with any or all of these keys
        gonzo = {
            'info_section': {dict} ,
            'command': {dict},
            'descriptors': [list of {dicts}],
            }

        * load doesn't need to be called directly
          unless you initialize a Cue without data.

        """
        if isinstance(gonzo, bytes):
            gonzo = gonzo.decode()
        if isinstance(gonzo, str):
            if gonzo.isdigit():
                gonzo = int(gonzo)
                self.bites = self._int_bits(int(gonzo))
                self.decode()
                return self.bites
            if gonzo.strip()[0] == "<":
                self._from_xml(gonzo)
                return self.bites
            gonzo = json.loads(gonzo)
        if "command" not in gonzo:
            self._no_cmd()
        self._load_info_section(gonzo)
        self._load_command(gonzo)
        self._load_descriptors(gonzo["descriptors"])
        self.encode()
        return self.bites

    def _from_xml(self, gonzo):
        """
        _from_xml converts xml to data that can
        be loaded by a Cue instance.
        """
        dat = xml2cue(gonzo)
        if isinstance(
            dat, str
        ):  # a string  is returned for Binary xml tag, make sense?
            self.bites = self._mk_bits(dat)
            self.decode()
        else:
            self.load(dat)  # a dict is returned for infosection xml.
            # Self.encode() will calculate lengths and types and such
        #  self.encode()

    def _xml_mk_descriptor(self, sis, ns):
        """
        _mk_descriptor_xml make xml nodes for descriptors.
        """
        for d in self.descriptors:
            if d.has("segmentation_type_id"):
                if d.segmentation_type_id in table22:
                    comment = f"{table22[d.segmentation_type_id]}"
                    sis.add_comment(comment)
                else:
                    d.errors.append("Segmentation type id not in table 22")
            sis.add_child(d.xml(ns=ns))
        return sis

    def xml(self, ns="scte35"):
        """
        xml returns a threefive3.Node instance
        which can be edited as needed or printed.
        xmlbin
        """
        sis = self.info_section.xml(ns=ns)
        cmd = self.command.xml(ns=ns)
        sis.add_child(cmd)
        sis = self._xml_mk_descriptor(sis, ns)
        sis.mk()
        return sis

    def xmlbin(self, ns="scte35"):
        """
        xml returns a threefive3.Node instance
        which can be edited as needed or printed.
        xmlbin
        """
        sig_attrs = {"xmlns": "https://scte.org/schemas/35"}
        sig_node = Node("Signal", attrs=sig_attrs, ns=ns)
        bin_node = Node("Binary", value=self.encode(), ns=ns)
        sig_node.add_child(bin_node)
        return sig_node
