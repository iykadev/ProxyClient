import json
from queue import Queue

import client_manager
import client_module_handler as mh
import client_packet
from log import log


class ModuleManager(client_manager.Manager):

    def __init__(self, srvrhndlr):
        self.srvrhndlr = srvrhndlr
        self.requests_queue = Queue()
        self.module = None

    def _request_module_data(self):
        data = json.dumps(dict(data="SEND_FUNCTION_DATA"))
        pk = client_packet.Packet(data, client_packet.PACKET_ID_FUNC_INIT)
        self.srvrhndlr.send_packet(pk)

    def handle_request(self, packet_id, data):

        if packet_id is client_packet.PACKET_ID_FUNC_INIT:
            module_name, module_construct = mh.construct_module(data.get_data())

            # File written module
            #mh.generate_module_file(module_name, module_construct)
            #self.module = mh.load_module(module_name, self)
            #log(module_construct)
            self.module = mh.compile_module(module_name, module_construct, self.srvrhndlr)
        elif packet_id is client_packet.PACKET_ID_FUNC_CALL:
            pass
        elif packet_id is client_packet.PACKET_ID_FUNC_CALL_RETURN:
            data = int(data.get_data())
            self.module.results_queue.put(data)
        elif packet_id is client_packet.PACKET_ID_FUNC_CALL_ERROR:
            pass

    def init(self):
        self._request_module_data()

    def loop(self):
        pass
        # data = None
        # start_new_thread(self._handle_request, (self._receive_data(1),))
        # data = packet.Packet(self.requests_queue.get())
        # log(data)

    def responds_to(self, packet_id):
        return 0 <= packet_id < 100