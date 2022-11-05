import json
import logging

import netifaces as ni
from ipaddress import IPv4Interface
from threading import Lock


class NodeInfo:
    def __init__(self, node_type="init", address="init", name="unknown", json_data=None):

        if json_data is not None:
            self.__dict__ = json_data

            self.node_type = json_data['node_type']
            self.address = json_data['address']
            self.name = json_data['name']
            self.color = json_data['color']
            self.time = json_data['time']
            self.leader_start_time = json_data['leader_start_time']
            self.last_leader = json_data['last_leader']
            return
        self.node_type = node_type
        self.address = address
        self.name = name
        self.color = "none"
        self.time = 0
        self.leader_start_time = 0
        self.last_leader = None
        try:
            interface_info = ni.ifaddresses("eth1")[ni.AF_INET][0]
            ip_addr = interface_info['addr']
            netmask = interface_info['netmask']
            self.address = ip_addr
            self.interface = IPv4Interface(f'{ip_addr}/{netmask}')
        except ValueError as e:
            logging.error("Something failed during node interface init: %s" % e)
            self.interface = None
        self.promotedAsLeader = False
        self.colorLock = Lock()
        self.leaderSearchRetryCount = 0
        self.assignedColorCount = 0

    def to_string(self):
        # convert to JSON format
        return json.dumps({
            "node_type": self.node_type,
            "address": self.address,
            "name": self.name,
            "color": self.color,
            "time": self.time,
            "leader_start_time": self.leader_start_time,
            "last_leader": self.last_leader
        })


def json_from_string(json_data):

    try:
        return json.loads(json_data)
    except TypeError:
        return None

