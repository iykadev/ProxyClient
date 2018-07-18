import socket

import manager

from log import log


class ReceptionManager(manager.Manager):

    def __init__(self, srvrhndlr, managers):
        self.srvrhndlr = srvrhndlr
        self.managers = managers
        self.thread = None

    def _handle_reception(self, initial_data):
        data = self.srvrhndlr.handle_receiving_data(initial_data)

        try:
            packet_id = data.packet_id

            for manager in self.managers:
                if manager.responds_to(packet_id):
                    manager.handle_request(packet_id, data)
                    break

        except Exception as e:
            if str(e) == "[WinError 10035] A non-blocking socket operation could not be completed immediately":
                return

            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
            self.srvrhndlr.isConnected = False

    def init(self):
        pass

    def loop(self):
        self.srvrhndlr.socket.setblocking(0)
        try:
            self._handle_reception(self.srvrhndlr.receive_data(1))
        except socket.error as e:
            if str(e) == "[WinError 10035] A non-blocking socket operation could not be completed immediately":
                return

            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
            self.srvrhndlr.isConnected = False
        self.srvrhndlr.socket.setblocking(0)

