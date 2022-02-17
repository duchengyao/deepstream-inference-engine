import argparse
import json

from flask import Flask, request

from tsif import TSIF

from configs import config_flask as config

app = Flask(__name__)
tsif = TSIF("configs/official-yolov5n/config_infer_primary_yoloV5.txt")


@app.route('/add_source', methods=['GET'])
def add_source():
    try:
        source_id = request.form['ID']
        uri = request.form['URI']
        print(uri)
        tsif.add_source(uri)
        return json.dumps({"stat": 0, "desc": "Add new source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


@app.route('/del_source', methods=['GET'])
def remove_source():
    try:
        source_id = request.form['ID']

        return json.dumps({"stat": 0, "desc": "Remove source: " + str(source_id)})
    except Exception as e:
        return json.dumps({"stat": -1, "desc": str(e)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true')
    args = parser.parse_args()

    tsif.start()

    app.run(host=config.ADDRESS,
            port=config.PORT,
            debug=args.debug)
