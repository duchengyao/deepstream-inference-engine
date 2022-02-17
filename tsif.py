import argparse
import time
import _thread as thread
import sys

import gi

gi.require_version('Gst', '1.0')  # noqa: E402
gi.require_version('GstRtspServer', '1.0')  # noqa: E402
gi.require_version("GstVideo", "1.0")  # noqa: E402

from gi.repository import GObject, Gst, GstRtspServer, GLib, GstVideo
from common.ds_utils import bus_call, is_aarch64, GetFPS
from common.create_pipeline import create_pipeline
from common.gs_utils import create_source_bin


class TSIF:
    def __init__(self,
                 infer_config,
                 batch_size=16,
                 codec="H264",
                 gie="nvinfer",
                 updsink_port_num=5400,
                 rtsp_port_num=8554):

        self.max_source_id = -1

        GObject.threads_init()
        Gst.init(None)
        self.pipeline, self.loop, self.streammux = create_pipeline(
            batch_size, 4000000, codec, batch_size, "nvinfer", updsink_port_num,
            infer_config
        )

        # Start streaming
        server = GstRtspServer.RTSPServer.new()
        server.props.service = "%d" % rtsp_port_num
        server.attach(None)

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(
            '( udpsrc name=pay0 port=%d buffer-size=524288 '
            'caps="application/x-rtp, media=video, clock-rate=90000, '
            'encoding-name=(string)%s, payload=96 " )'
            % (updsink_port_num, codec)
        )
        factory.set_shared(True)
        server.get_mount_points().add_factory("/ds-test", factory)

        print(
            "\n *** DeepStream: Launched RTSP Streaming at "
            "rtsp://localhost:%d/ds-test ***\n\n"
            % rtsp_port_num
        )

        # start play back and listen to events
        print("Starting pipeline \n")
        self.pipeline.set_state(Gst.State.PLAYING)

    def start(self):
        try:
            thread.start_new_thread(self.loop.run, ())
        except Exception as e:
            # TODO: log Fatal
            print(e)

    def cleanup(self):
        self.pipeline.set_state(Gst.State.NULL)

    def add_source(self, uri_name):
        print("Creating source_bin ", uri_name, " \n ")
        self.max_source_id += 1
        source_bin = create_source_bin(self.max_source_id, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")
        self.pipeline.add(source_bin)
        padname = "sink_%u" % self.max_source_id
        sinkpad = self.streammux.get_request_pad(padname)
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad = source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)
        source_bin.set_state(Gst.State.PLAYING)


if __name__ == '__main__':
    inputs = [
        "rtsp://localhost:8550/stream0",
        "rtsp://localhost:8550/stream1",
        "rtsp://localhost:8550/stream0",
        "rtsp://localhost:8550/stream1",
        "rtsp://localhost:8550/stream0",
        "rtsp://localhost:8550/stream1",
        "rtsp://localhost:8550/stream0",
        "rtsp://localhost:8550/stream1"
    ]

    tsif = TSIF("configs/official-yolov5n/config_infer_primary_yoloV5.txt")

    tsif.start()
    tsif.add_source(inputs[0])
    time.sleep(100)
