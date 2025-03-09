#!/usr/bin/env python3

"""

gums, Grande Unicast Multicast Sender


"""
import argparse
import os
import socket
import sys
import time
from functools import partial
from .new_reader import reader


DGRAM_SIZE = 1316
THIRTY_DGRAMS = 30 * DGRAM_SIZE

DEFAULT_MULTICAST = "235.35.3.5:3535"


REV = "\033[7m"
NORM = "\033[27m"


class GumS:
    """
    GumS class is the UDP Unicast/Multicast Sender
    """

    def __init__(self, addr=None, mttl=16, bind_addr="0.0.0.0"):
        self.dest_ip, self.dest_port = addr.rsplit(":", 1)
        self.src_ip = bind_addr.rsplit(":", 1)[0]
        self.src_port = 0
        self.ttl = mttl
        self.dest_grp = (self.dest_ip, int(self.dest_port))
        self.sock = self.mk_sock()
        self.sock.bind((self.src_ip, self.src_port))

    def is_multicast(self):
        """
        is_multicast tests the first byte of an ipv4 address
        to see if it is in the multicast range.
        """
        net_id = int(self.dest_ip.split(".", 1)[0])
        if net_id in range(224, 240):
            return True
        return False

    def mk_sock(self):
        """
        mk_sock makes a udp socket, self.sock
        and sets a few opts.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        return sock

    def iter_dgrams(self, vid):
        """
        iter_dgrams iterates over the video and sends
        self.dgram_size chunks of video to the socket.
        """
        million = 1024 * 1024
        start_time = time.time()
        time.sleep(0.0001)
        now = time.time
        total_bytes = 0
        with reader(vid) as gum:
            for dgram in iter(partial(gum.read, THIRTY_DGRAMS), b""):
                self.sock.sendto(dgram, self.dest_grp)
                total_bytes += len(dgram)
                elapsed = now() - start_time
                rate = (total_bytes / million) / elapsed
                print(
                    f"\t{total_bytes/million:0.2f} MB sent in {elapsed:5.2f} seconds. {rate:3.2f} MB/Sec",
                    end="\r",
                    file=sys.stderr,
                )
            print("\n", file=sys.stderr)

    def send_stream(self, vid):
        """
        send_stream sets multicast ttl if needed,
        prints socket address info,
        calls self.iter_dgrams,
        and closes the socket
        """
        proto = "udp://"
        pre = "Unicast"
        if self.is_multicast():
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)
            proto = proto + "@"
            pre = "Multicast"
        src_ip, src_port = self.sock.getsockname()
        print(
            f"\n\t{pre} Stream\n\t{proto}{self.dest_ip}:{self.dest_port}",
            file=sys.stderr,
        )
        print(f"\n\tSource\n\t{src_ip}:{src_port}\n", file=sys.stderr)

        self.iter_dgrams(vid)
        self.sock.close()


def parse_args():
    """
    parse_args parse command line args
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default=sys.stdin.buffer,
        help=f"""like "/home/a/vid.ts"
                or "udp://@235.35.3.5:3535"
                or "https://futzu.com/xaa.ts"
                [default:{REV}sys.stdin.buffer{NORM}]
             """,
    )

    parser.add_argument(
        "-a",
        "--addr",
        default=DEFAULT_MULTICAST,
        help=f"Destination IP:Port  [default:{REV}235.35.3.5:3535{NORM}]",
    )

    parser.add_argument(
        "-b",
        "--bind_addr",
        default="0.0.0.0",
        help=f" Local IP to bind [default:{REV}0.0.0.0{NORM}]",
    )

    parser.add_argument(
        "-t",
        "--ttl",
        default=32,
        help=f"Multicast TTL (1 - 255) [default:{REV}32{NORM}]",
    )

    return parser.parse_args()


def fork():
    """
    fork
    """

    pid = os.fork()
    if pid > 0:
        sys.exit(0)


def daemonize():
    """
    The Steven's double fork
    """

    fork()
    fork()


def cli():
    """
    cli adds command line args
    passes them to a Gums instance
    and calls self.send_stream
    in just one function call

    Use like this

    import gums

    if __name__ == "__main__":
        gums.cli()


    """

    args = parse_args()
    #  daemonize()
    ttl = int(args.ttl).to_bytes(1, byteorder="big")
    dest_addr = args.addr
    gummie = GumS(dest_addr, ttl, args.bind_addr)
    gummie.send_stream(args.input)
    sys.exit()


if __name__ == "__main__":
    cli()
