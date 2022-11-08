import threading
import time
import logging
import requests
import json

# time in seconds
PING_PERIOD = 5
MAX_RETRY = 5
CLIENT_SLEEP_TIME = 2
MAX_OUTAGE_TIME = 10

OK_RESPONSE = "{'response':'Ok'}"
NOT_LEADER_RESPONSE = "{'response':'NotLeader'}"

COLOR_NONE = "none"
COLOR_GREEN = "green"
COLOR_RED = "red"

INIT_TYPE = "init"
SLAVE_TYPE = "slave"
COLORED_SLAVE_TYPE = "colorSlave"
LEADER_TYPE = "leader"


class MasterSelectorThread(threading.Thread):
    def __init__(self, node, receiver):
        threading.Thread.__init__(self)
        self.actual_node = node
        self.runningFlag = True
        self.receiver = receiver
        self.color_map = {}

    # helper function to execute the threads
    def run(self):
        while self.runningFlag:
            # check last pings for possible node removal

            self.check_active_nodes()
            if self.actual_node.promotedAsLeader:
                # logging.debug("Im boss!")

                active_nodes = self.receiver.get_active_nodes()
                if active_nodes is None:
                    return

                elif len(self.color_map) == len(active_nodes):
                    with self.actual_node.colorLock:
                        colors = json.dumps(self.color_map, indent=4)
                        logging.info(
                            "Everyone is colored! I as leader have green color and node color assignment looks like this: \n %s" % colors)
                else:
                    logging.info("Waiting for everyone to get colored")
                time.sleep(CLIENT_SLEEP_TIME)
            elif self.actual_node.last_leader is None:
                self.look_for_leader()
            elif self.actual_node.color == COLOR_NONE:
                self.ask_for_color()
            else:
                # im finished :-)
                logging.debug("Im finished!")
                time.sleep(CLIENT_SLEEP_TIME)
            time.sleep(CLIENT_SLEEP_TIME)

    def assign_color(self, address):
        with self.actual_node.colorLock:

            if address in self.color_map.keys():
                color = self.color_map[address]
                logging.debug("Assigning again color %s to the known node %s " % (color, address))
                return color
            else:
                green_count = sum(1 for v in self.color_map.values() if v == COLOR_GREEN)
                map_len = len(self.color_map)
                if map_len == 0 or (green_count + 1.0) / len(self.color_map) > 1 / 3:
                    color = COLOR_RED
                else:
                    color = COLOR_GREEN
                self.color_map[address] = color
                logging.info("Assigning color %s to the newly connected node %s " % (color, address))

                return color

    def find_address_by_color(self, color):
        for clrAddr, clrColor in self.color_map.items():
            if clrColor == color:
                return clrAddr
        return None

    def check_active_nodes(self):

        actual_time = time.time()
        active_nodes = self.receiver.get_active_nodes()
        if active_nodes is None:
            return

        for address, node in active_nodes.items():
            if actual_time - node.time > MAX_OUTAGE_TIME:
                logging.info("Removing non active node %s !" % address)
                self.receiver.remove_nonactive_node(address)
                if self.actual_node.promotedAsLeader:
                    self.check_color_integrity(address)
                else:
                    if self.actual_node.last_leader['address'] == address:
                        logging.info("Oh no, my leader is out! ")
                        self.actual_node.last_leader = None
                        self.actual_node.color = COLOR_NONE
                        self.actual_node.node_type = INIT_TYPE

            else:
                if self.actual_node.promotedAsLeader and node.node_type == LEADER_TYPE:
                    if self.actual_node.leader_start_time < node.leader_start_time:
                        logging.info("Challenging node %s because i am more suitable leader (enemy:%s > me:%s)!"
                                     % (address, node.leader_start_time, self.actual_node.leader_start_time))
                        self.challenge_to_fight(node.address)
                    else:
                        logging.info("Leader %s is more suitable leader than me (%s > %s)!"
                                     % (address, self.actual_node.leader_start_time, node.leader_start_time))
                        self.actual_node.promotedAsLeader = False
                        self.actual_node.last_leader = {'address': node.address, "time": node.leader_start_time}
                        self.actual_node.node_type = SLAVE_TYPE

    def check_color_integrity(self, address):
        # was the green/red ratio changed?
        with self.actual_node.colorLock:
            self.color_map.pop(address)
            map_len = len(self.color_map)
            if map_len == 0:
                return
            green_count = sum(1 for v in self.color_map.values() if v == COLOR_GREEN)
            ratio = (float(green_count) + 1.0) / float(map_len + 1)
            logging.info("GREEN/RED ratio is currently %s" % ratio)
            if ratio < 1/3:
                color = COLOR_GREEN
                address = self.find_address_by_color(COLOR_RED)
            elif ratio >= 2/3:
                color = COLOR_RED
                address = self.find_address_by_color(COLOR_GREEN)
            else:
                return
            if address is None:
                return
            logging.info("Color integrity was compromised by the outage. Assigning color %s to node %s"
                         % (color, address))
            self.assign_new_color(address, color)

    def assign_new_color(self, address, color):

        try:
            redraw_json = {'address': self.actual_node.address, "color": color}
            res_address = "http://" + address + ":5000/assignColor/"
            logging.debug("Sending HTTP POST to %s " % res_address)
            x = requests.post(res_address, json=redraw_json).text
            logging.info("My slave node responded: %s" % x)
            if x == OK_RESPONSE:
                # he is no longer leader => ok
                self.color_map[address] = color
                return
            else:
                logging.error("Unknown response from enemy leader (%s)!" % address)
                return
        except Exception as e:
            logging.error("Redrawing of new color to the node %s failed due to %s" % (address, e))

    def challenge_to_fight(self, address):
        try:
            challenge_json = {'address': self.actual_node.address, "time": self.actual_node.leader_start_time}

            res_address = "http://" + address + ":5000/fight/"
            logging.debug("Sending HTTP POST to %s " % res_address)
            x = requests.post(res_address, json=challenge_json).text
            logging.info("Enemy leader responded: %s" % x)
            if x == OK_RESPONSE or x == NOT_LEADER_RESPONSE:
                # he is no longer leader => ok
                return
            else:
                logging.error("Unknown response from enemy leader (%s)!" % address)
                return
        except Exception as e:
            logging.error("Challenging node %s failed due to %s" % (address, e))

    def look_for_leader(self):
        logging.info("Looking for a leader for the %s . time!" % (self.actual_node.leaderSearchRetryCount + 1))
        if self.actual_node.leaderSearchRetryCount + 1 >= MAX_RETRY:
            self.actual_node.promotedAsLeader = True
            self.actual_node.leaderSearchRetryCount = 0
            self.actual_node.assignedColorCount = 0
            time_key = time.time()
            self.actual_node.leader_start_time = time_key
            logging.info("Becoming leader because there are no suitable candidates (time key %s)" % time_key)
            self.actual_node.node_type = LEADER_TYPE
            self.actual_node.color = COLOR_NONE
            self.actual_node.last_leader = {'address': self.actual_node.address,
                                            "time": self.actual_node.leader_start_time}

        else:
            # look for possible leaders
            active_nodes = self.receiver.get_active_nodes()
            if active_nodes is None:
                return

            for address, node in active_nodes.items():
                if node.node_type == LEADER_TYPE:
                    if self.actual_node.last_leader is None \
                            or self.actual_node.last_leader['time'] > node.leader_start_time:
                        logging.info("Found suitable leader on %s with time key %s"
                                     % (node.address, node.leader_start_time))
                        self.actual_node.leaderSearchRetryCount = 0
                        self.actual_node.last_leader = {'address': node.address,
                                                        "time": node.leader_start_time}
            self.actual_node.leaderSearchRetryCount += 1

    def ask_for_color(self):
        try:
            logging.info("Asking leader for color")

            address_json = {'address': self.actual_node.address}

            res_address = 'http://' + self.actual_node.last_leader['address'] + ":5000/askForColor/"
            logging.debug("Sending HTTP POST to %s " % res_address)
            x = requests.post(res_address, json=address_json).text

            if x == NOT_LEADER_RESPONSE:
                # node we contacted is no longer leader
                self.actual_node.last_leader = None
                self.actual_node.node_type = INIT_TYPE
                self.actual_node.color = COLOR_NONE
                self.actual_node.leaderSearchRetryCount = 0
                logging.info("Leader is no longer valid and cant assign me color. Changing to INIT state")
            elif x == COLOR_GREEN or x == COLOR_RED:
                logging.info("Leader assigned me color %s" % x)
                self.actual_node.node_type = COLORED_SLAVE_TYPE
                self.actual_node.color = x
            else:
                logging.error("Leader sent me unknown response: " + x)
        except Exception as e:
            logging.error("Asking for color failed due to %s" % e)
