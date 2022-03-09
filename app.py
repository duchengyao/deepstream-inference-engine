import argparse
import json

from flask import Flask, request

from core.engine import Engine

from configs import global_config

app = Flask(__name__)

str2id = {}


@app.route('/add_source', methods=['POST'])
def add_source():
    try:
        device_id = request.form['device_id']
        assert device_id not in str2id.keys(), "Duplicate ID detected."
        source_id = None
        for i in range(128):
            if i not in str2id.values():
                source_id = i
                str2id[device_id] = source_id
                break
        assert source_id is not None, "Exceeding the resource limit, " \
                                      "the number of devices must be less than 128."

        uri = request.form['rtsp_url']
        grpc_address = request.form['address']

        tsif.add_source(uri, source_id, grpc_address, device_id)
        return json.dumps({"stat": 0, "desc": "Add new source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


@app.route('/remove_source', methods=['DELETE'])
def remove_source():
    try:
        device_id = request.form['device_id']
        assert device_id in str2id.keys(), "Cannot find ID."
        source_id = str2id[device_id]
        str2id.pop(device_id)
        tsif.remove_source(source_id)
        return json.dumps({"stat": 0, "desc": "Remove source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("algo", type=str, help="{phone_call_detect,jam_detect}")
    parser.add_argument("-d", "--debug", action='store_true')
    parser.add_argument("--rtsp_port_num",type=int, default=8554, help='core.engine.rtsp_port_num')
    args = parser.parse_args()

    tsif = Engine(args.algo)

    app.run(host=global_config.FLASK_ADDRESS,
            port=global_config.FLASK_PORT,
            debug=args.debug,
            rtsp_port_num=engine.rtsp_port_num)
