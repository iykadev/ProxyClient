import socket

from log import log
from socket_handler import Handler


class Server(Handler):

    def __init__(self, self_name=None, peer_name=None, conn=None, self_ip=None, self_port=None, peer_ip=None, peer_port=None, call_back=None, call_back_args=None):
        super().__init__(self_name=self_name, peer_name=peer_name, conn=conn, self_ip=self_ip, self_port=self_port, peer_ip=peer_ip, peer_port=peer_port, call_back=call_back, call_back_args=call_back_args)

        #TODO remove debug line
        self.log_coms = False

def init_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((ip, port))
    except socket.error:
        log("Could not connect to", ip + ":" + str(port))

    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    return s


def generate_handler(self_name=None, peer_name=None, conn=None, self_ip=None, self_port=None, peer_ip=None, peer_port=None, call_back=None, call_back_args=None):
    return Server(self_name=self_name, peer_name=peer_name, conn=conn, self_ip=self_ip, self_port=self_port, peer_ip=peer_ip, peer_port=peer_port, call_back=call_back, call_back_args=call_back_args)
