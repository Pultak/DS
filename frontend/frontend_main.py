from flask import Flask
import json

from client import receiver_thread

app = Flask(__name__)

receiver = receiver_thread.NodeInfoReceiverThread()
receiver.run()
receiver.join()


@app.route('/nodes')
def get_nodes():
    return json.dumps(receiver.addressDict, indent=4)
