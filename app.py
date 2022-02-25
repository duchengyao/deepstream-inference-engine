import argparse
import json

from flask import Flask, request

from core.engine import Engine

from configs import global_config

app = Flask(__name__)
tsif = Engine("phone_call_detect")


@app.route('/add_source', methods=['POST'])
def add_source():
    try:
        source_id = int(request.form['ID'])
        uri = request.form['URI']
        tsif.add_source(uri, source_id)
        return json.dumps({"stat": 0, "desc": "Add new source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


@app.route('/remove_source', methods=['DELETE'])
def remove_source():
    try:
        source_id = int(request.form['ID'])
        tsif.remove_source(source_id)
        return json.dumps({"stat": 0, "desc": "Remove source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true')
    args = parser.parse_args()
    app.run(host=global_config.FLASK_ADDRESS,
            port=global_config.FLASK_PORT,
            debug=args.debug)
