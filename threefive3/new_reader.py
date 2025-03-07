"""
new_reader.py
Home of the reader function
"""

import socket
import struct
import sys
import urllib.request
from .stuff import blue

TIMEOUT = 60


class Socked(socket.socket):
    """
    Socked class subclasses socket.socket
    and defines a read() method to maintain the interface.
    """

    def read(self, bites):
        """
        read is an alias for socket.socket.recv
        """
        return self.recv(bites)


def reader(uri, headers={}):
    """
    reader returns an open file handle.
    stdin:              cat video.ts | gumd
    files:              "/home/you/video.ts"
    http(s) urls:       "https://example.com/vid.ts"
     (http headers can be added by setting headers)
    udp urls:           "udp://1.2.3.4:5555"
    multicast urls:     "udp://@227.1.3.10:4310"

    Use like:

    with reader('http://iodisco.com/') as disco:
        disco.read()

    with reader('http://iodisco.com/',headers={"myHeader":"DOOM"}) as doom:
        doom.read()

    with reader("udp://@227.1.3.10:4310") as data:
        data.read(8192)

    with reader("/home/you/video.ts") as data:
        fu = data.read()

    udp_data =reader("udp://1.2.3.4:5555")
    chunks = [udp_data.read(188) for i in range(0,1024)]
    udp_data.close()

    """
    # read from stdin
    if uri in [None, sys.stdin.buffer]:
        return sys.stdin.buffer
    # Multicast
    if uri.startswith("udp://@"):
        return _open_mcast(uri)
    # Udp
    if uri.startswith("udp://"):
        return _open_udp(uri)
    # Http(s)
    if uri.startswith("http"):
        req = urllib.request.Request(uri, headers=headers)
        return urllib.request.urlopen(req)
    # File
    return open(uri, "rb")


def lshiftbuf(socked):
    shift = 2
    rcvbuf_size = socked.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    try:
        rcvbuf_size = rcvbuf_size << shift
        socked.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuf_size)
        blue(f" socket.SO_RCVBUF left shifted  to {rcvbuf_size}")
    except:
        blue("Unable to left shift socket.SO_RCVBUF")


def _mk_socked():
    socked = Socked(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    lshiftbuf(socked)
    socked.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        socked.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    socked.settimeout(TIMEOUT)
    return socked


def _mk_udp_sock(udp_ip, udp_port):
    """
    udp socket setup
    """
    udp_sock = _mk_socked()
    udp_sock.bind((udp_ip, udp_port))
    return udp_sock


def _open_udp(uri):
    """
    udp://1.2.3.4:5555
    """
    udp_ip, udp_port = (uri.split("udp://")[1]).rsplit(":", 1)
    udp_port = int(udp_port)
    return _mk_udp_sock(udp_ip, udp_port)


def _open_mcast(uri):
    """
    udp://@227.1.3.10:4310
    """
    interface_ip = "0.0.0.0"
    multicast_group, port = (uri.split("udp://@")[1]).rsplit(":", 1)
    multicast_port = int(port)
    socked = _mk_socked()
    socked.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 32))
    socked.bind(("", multicast_port))
    socked.setsockopt(
        socket.SOL_IP,
        socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(multicast_group) + socket.inet_aton(interface_ip),
    )
    return socked
