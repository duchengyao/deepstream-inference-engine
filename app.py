import argparse
import json

from flask import Flask, request

from core.engine import Engine
from common.stupid_global_var import device2source, update_device_dict

app = Flask(__name__)


@app.route('/add_source', methods=['POST'])
def add_source():
    try:
        # TODO: 如果添加资源失败，deviceID也会被占用
        device_id = request.form['device_id']
        assert device_id not in device2source.keys(), "Duplicate ID detected."
        source_id = None
        for i in range(128):
            if i not in device2source.values():
                source_id = i
                device2source[device_id] = source_id
                update_device_dict()
                break
        assert source_id is not None, "Exceeding the resource limit, " \
                                      "the number of devices must be less than 128."

        uri = request.form['rtsp_url']
        grpc_address = request.form['grpc_address']

        ie.add_source(uri, source_id, grpc_address)
        return json.dumps({"stat": 0, "desc": "Add new source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


@app.route('/remove_source', methods=['DELETE'])
def remove_source():
    try:
        device_id = request.form['device_id']
        assert device_id in device2source.keys(), "Cannot find ID."
        source_id = device2source[device_id]
        device2source.pop(device_id)
        update_device_dict()
        ie.remove_source(source_id)
        return json.dumps({"stat": 0, "desc": "Remove source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("algo", type=str, help="{phone_call_detect, jam_detect}")
    parser.add_argument("-d", "--debug", action='store_true')
    parser.add_argument("--flask_address", type=str, default="0.0.0.0")
    parser.add_argument("--flask_port", type=int, default=19878)
    parser.add_argument("--rtsp_port", type=int, default=8554)
    args = parser.parse_args()

    ie = Engine(args.algo, rtsp_port_num=args.rtsp_port)

    app.run(host=args.flask_address,
            port=args.flask_port,
            debug=args.debug)
