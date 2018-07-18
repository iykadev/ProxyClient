import socket
import sys

import client_packet
import client_thread
from log import log


client_name = "CLIENT"

SHOW_SOCKET_COMS = True


class Server:

    def __init__(self, socket=None, server_name=None, host=None, port=None, call_back=None, call_back_args=None):
        self.isConnected = True;
        self.socket = socket
        self.server_name = server_name
        self.host = host
        self.port = port
        self.call_back = call_back
        self.call_back_args = call_back_args

    # sends packet to connection
    def _send_packet(self, packet):
        self.socket.sendall(packet.export())

    # receives a packet from client and adds it to a queue
    def _receive_packet(self, buffer_length):
        return client_packet.Packet(self.socket.recv(buffer_length))

    def _receive_data(self, buffer_length):
        return self.socket.recv(buffer_length)

    # wrapper for packet sending
    def send_packet(self, packet):
        self._send_packet(packet)
        if SHOW_SOCKET_COMS:
            log("<%s>" % client_name, packet, '\n')

    # wrapper for packet receiving
    def receive_packet(self, buffer_length):
        packet = self._receive_packet(buffer_length)
        if SHOW_SOCKET_COMS:
            log("<%s>" % self.server_name, packet, '\n')
        return packet

    def receive_data(self, buffer_length):
        return self._receive_data(buffer_length)

    def handle_receiving_data(self, initial_data):
        data = initial_data.decode('utf8')
        while len(data) < len(client_packet.STREAM_TERMINATING_BYTE) or data[-len(client_packet.STREAM_TERMINATING_BYTE):] != client_packet.STREAM_TERMINATING_BYTE.decode(
                'utf8'):
            data += self.receive_data(1).decode('utf8')

        data = data[:-len(client_packet.STREAM_TERMINATING_BYTE)]
        data = client_packet.Packet(str.encode(data))

        if SHOW_SOCKET_COMS:
            log("<%s>" % self.server_name, data, '\n')

        return data

    def handle_connection(self):
        thread = client_thread.CThread(self.call_back, (self, *self.call_back_args), is_daemon=False)
        thread.start()
        return thread

    def print_connection_info(self):
        log('connected to:', self.host + ":" + str(self.port))

    def print_disconnection_info(self):
        log("Connection lost with host:", self.host + ":" + str(self.port))

    def disconnect(self):
        self.socket.shutdown(socket.SHUT_WR)


def init_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
    except socket.error:
        log("Could not connect to", host + ":" + str(port))
        sys.exit(1)

    return s


def generate_server_handler(socket=None, server_name=None, host=None, port=None, call_back=None, call_back_args=None):
    return Server(socket=socket, server_name=server_name, host=host, port=port, call_back=call_back, call_back_args=call_back_args)


def set_client_name(name):
    global client_name

    client_name = name