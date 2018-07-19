import socket

import manager
from log import log


class ReceptionManager(manager.Manager):

    def __init__(self, srvrhndlr, managers):
        self.srvrhndlr = srvrhndlr
        self.managers = managers
        self.thread = None

    def _handle_reception(self):
        data = self.srvrhndlr.handle_receiving_data()

        packet_id = data.packet_id

        for man in self.managers:
            if man.responds_to(packet_id):
                man.handle_request(packet_id, data)
                break

    def init(self):
        pass

    def loop(self):
        self.srvrhndlr.conn.setblocking(0)
        try:
            self._handle_reception()
        except socket.error as e:
            if str(e) == "[WinError 10035] A non-blocking socket operation could not be completed immediately":
                return

            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
            self.srvrhndlr.isConnected = False