# import the threading module
import threading
import logging

from threading import Lock
import socket

import node_info
from node_info import NodeInfo


class NodeInfoReceiverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

        self.addressDict = {}
        self.nodeInfo = NodeInfo()
        self.lock = Lock()

    # helper function to execute the threads
    def run(self):

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Enable broadcasting mode
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        client.bind(("", 37020))
        # self_address =

        while True:
            try:
                data, addr = client.recvfrom(1024)

                decoded_data = data.decode("ascii")
                if decoded_data[0] == '{':
                    self.parse_broadcast_input(data, addr)
            except Exception as e:
                logging.error("Exception found inside receiver thread! %s" % e)

    def parse_broadcast_input(self, data, addr):
        parsed_json = node_info.json_from_string(data)
        parsed_info = None
        if parsed_json is not None:
            parsed_info = NodeInfo(json_data=parsed_json)
        if parsed_info is not None and parsed_info:
            logging.debug("(%s-%s) is of type %s" % (parsed_info.address, parsed_info.name, parsed_info.node_type))

            if self.nodeInfo.address != parsed_info.address:
                if parsed_info.address not in self.addressDict.keys():
                    logging.info("New node connected to our network! Address %s" % parsed_info.address)

                self.addressDict[parsed_info.address] = parsed_info

    def add_new_node(self, address, node):
        # acquire the lock
        with self.lock:
            self.addressDict[address] = node

    # remove some items from the shared dictionary
    def remove_nonactive_node(self, key):
        # acquire the lock
        with self.lock:
            if key in self.addressDict.keys():
                self.addressDict.pop(key)

    def get_active_nodes(self):
        with self.lock:
            if len(self.addressDict) > 0:

                return dict(self.addressDict)
            else:
                return None

