import json


class NodeInfo:
    def __init__(self, node_type="init", address="init", json_data=None):

        if json_data is not None:
            self.__dict__ = json_data
            return
        self.node_type = node_type
        self.address = address
        self.color = "none"
        self.time = 0
        self.leader_start_time = 0

    def to_string(self):
        # convert to JSON format
        return json.dumps(self.__dict__)


def json_from_string(json_data):

    try:
        return json.loads(json_data)
    except TypeError as e:
        return None


def validate_json(json_data):
    schema = {
        "name": "string",
        "type": "string",
        "port": "number",
        "address": "string",
        "red_color": "boolean"
    }

    # todo add validation
    return True
