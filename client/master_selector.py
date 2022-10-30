# import the threading module
from client import broadcast_signaler, receiver_thread, node_info
import socket
import time
import requests

from flask import Flask, jsonify, request

app = Flask(__name__)
actual_node = node_info.NodeInfo(node_type="init", address=socket.gethostbyname(socket.gethostname()))


# time in seconds
PING_PERIOD = 2
MAX_OUTAGE_TIME = 20
CLIENT_SLEEP_TIME = 1

OK_RESPONSE = "{'response':'Ok'}"
NOT_LEADER_RESPONSE = "{'response':'NotLeader'}"

INIT_TYPE = "init"
SLAVE_TYPE = "slave"
LEADER_TYPE = "leader"

COLOR_NONE = "none"
COLOR_GREEN = "green"
COLOR_RED = "red"

EMPTY_LEADER = {'address': "0.0.0.0", "time": 0}


lastLeader = EMPTY_LEADER
promotedAsLeader = False
runningFlag = True


@app.route('/fight/', methods=['POST'])
def get_challenged():
    try:
        global lastLeader, promotedAsLeader
        new_challenger = request.get_json()

        if lastLeader is not None and lastLeader['time'] > new_challenger['time']:
            lastLeader = new_challenger
            promotedAsLeader = False
            actual_node.node_type = SLAVE_TYPE
            actual_node.leader_start_time = new_challenger['time']
            actual_node.color = COLOR_NONE
            return OK_RESPONSE
        else:
            return NOT_LEADER_RESPONSE
    except Exception as e:
        return "What are you trying to do? %s" % e


@app.route('/color/', methods=['POST'])
def get_colored():
    try:
        global lastLeader
        new_color_rq = request.get_json()

        if new_color_rq['address'] is lastLeader['address']:
            actual_node.color = new_color_rq['color']
            return OK_RESPONSE
        else:
            return NOT_LEADER_RESPONSE
    except Exception as e:
        return "What are you trying to do? %s" % e


def main():
    bs = broadcast_signaler.BroadcastSignalerThread(PING_PERIOD)
    receiver = receiver_thread.NodeInfoReceiverThread()

    bs.start()

if __name__ == "__main__":
    main()
