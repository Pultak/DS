# import the threading module
import logging
import socket
import time

from flask import Flask, request, jsonify

import broadcast_signaler
import node_info
import receiver_thread
import master_selector

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level='INFO')
app = Flask(__name__)
# hack to let the vagrant setup eth1 interface for http server
time.sleep(2)
actual_node = node_info.NodeInfo(node_type=master_selector.INIT_TYPE, address=socket.gethostbyname(socket.gethostname()),
                                 name="nodeName")

bs = broadcast_signaler.BroadcastSignalerThread(master_selector.PING_PERIOD, actual_node)
receiver = receiver_thread.NodeInfoReceiverThread()
ms = master_selector.MasterSelectorThread(actual_node, receiver)


@app.route("/ping/", methods=["GET"])
def ping():
    return jsonify({'ip': request.remote_addr}), 200


@app.route('/fight/', methods=['POST'])
def get_challenged():
    try:
        new_challenger = request.get_json()
        logging.info("Someone challenged me from %s" % new_challenger)
        if new_challenger is actual_node.last_leader:
            # challenger is already leader
            logging.debug("%s challenger is already my leader!" % new_challenger)
            return master_selector.OK_RESPONSE
        elif actual_node.promotedAsLeader and actual_node.leader_start_time > new_challenger['time'] or\
                (actual_node.last_leader is not None and actual_node.last_leader['time'] > new_challenger['time']):
            # im not worthy leader or challenger is better leader than my leader
            actual_node.last_leader = new_challenger
            actual_node.promotedAsLeader = False
            actual_node.node_type = master_selector.SLAVE_TYPE
            actual_node.leader_start_time = new_challenger['time']
            actual_node.color = master_selector.COLOR_NONE
            logging.debug("I have accepted %s as my new leader!" % new_challenger)
            return master_selector.OK_RESPONSE
        else:
            logging.debug("Im no longer a leader so I dont need to fight you %s!" % new_challenger)
            return master_selector.NOT_LEADER_RESPONSE
    except Exception as e:
        logging.error("Failure during getting challenged: %s" % e)
        return "What are you trying to do? %s" % e


@app.route('/assignColor/', methods=['POST'])
def assign_colored():
    try:
        new_color_rq = request.get_json()

        if actual_node.last_leader is not None and new_color_rq['address'] == actual_node.last_leader['address']:
            actual_node.color = new_color_rq['color']
            return master_selector.OK_RESPONSE
        else:
            return master_selector.NOT_LEADER_RESPONSE
    except Exception as e:
        logging.error("Failure during color assignment from leader: %s" % e)
        return "What are you trying to do? %s" % e


@app.route('/askForColor/', methods=['POST'])
def return_color():

    if actual_node.promotedAsLeader:
        new_color_rq = request.get_json()
        assigned_color = ms.assign_color(new_color_rq['address'])
        return assigned_color

    else:
        return master_selector.NOT_LEADER_RESPONSE


if __name__ == "__main__":
    # app.run()

    logging.info('Welcome to master selector client. Executing helper threads')

    bs.start()
    receiver.start()
    ms.start()
    logging.info('All helper threads started. Now executing Flask server')

    if actual_node.interface is None:
        logging.info("Found no valid interface. Starting flask on localhost")
        app.run()
        ms.join()
    else:
        app.run(host=str(actual_node.interface.ip))
