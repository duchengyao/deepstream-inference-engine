import argparse
import sys
import gi

gi.require_version('Gst', '1.0')  # noqa: E402
gi.require_version('GstRtspServer', '1.0')  # noqa: E402
gi.require_version("GstVideo", "1.0")  # noqa: E402
from gi.repository import GObject, Gst, GstRtspServer, GLib, GstVideo
from common.ds_utils import bus_call, is_aarch64, GetFPS
from common.create_pipeline import create_pipeline
from common.gs_utils import create_source_bin

frame_count = {}
frame_call = {}

GPU_ID = 0
MIN_CONFIDENCE = 0
MAX_CONFIDENCE = 1
RTSP_PORT_NUM = 8554
UPDSINK_PORT_NUM = 5400
BATCH_SIZE = 16
max_source_id = -1


def parse_args():
    parser = argparse.ArgumentParser(
        description='RTSP Output Sample Application Help ')
    parser.add_argument(
        "-i", "--input",
        help="Path to input H264 elementry stream", nargs="+",
        default=["a"],
        required=True)
    parser.add_argument(
        "-g", "--gie", default="nvinfer",
        help="choose GPU inference engine type nvinfer or nvinferserver , "
             "default=nvinfer",
        choices=['nvinfer', 'nvinferserver'])
    parser.add_argument(
        "-c", "--codec", default="H264",
        help="RTSP Streaming Codec H264/H265 , default=H264",
        choices=['H264', 'H265'])
    parser.add_argument(
        "-b", "--bitrate", default=4000000,
        help="Set the encoding bitrate ", type=int)
    # Check input arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    return args


def add_source(uri_name):
    global max_source_id
    print("Creating source_bin ", uri_name, " \n ")
    max_source_id += 1
    source_bin = create_source_bin(max_source_id, uri_name)
    if not source_bin:
        sys.stderr.write("Unable to create source bin \n")
    pipeline.add(source_bin)
    padname = "sink_%u" % max_source_id
    sinkpad = streammux.get_request_pad(padname)
    if not sinkpad:
        sys.stderr.write("Unable to create sink pad bin \n")
    srcpad = source_bin.get_static_pad("src")
    if not srcpad:
        sys.stderr.write("Unable to create src pad bin \n")
    srcpad.link(sinkpad)
    source_bin.set_state(Gst.State.PLAYING)


def main():
    args = parse_args()

    fps_streams = {}
    number_sources = len(args.input)
    for i in range(0, number_sources):
        fps_streams["stream{0}".format(i)] = GetFPS(i)

    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    # Check input arguments
    # for i in range(0, len(args.input)):
    #     fps_streams["stream{0}".format(i)] = GETFPS(i)
    number_sources = len(args.input)

    global pipeline, loop, streammux
    pipeline, loop, streammux = create_pipeline(
        args, number_sources, UPDSINK_PORT_NUM,
        "configs/official-yolov5n/config_infer_primary_yoloV5.txt")

    # Start streaming
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % RTSP_PORT_NUM
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 '
        'caps="application/x-rtp, media=video, clock-rate=90000, '
        'encoding-name=(string)%s, payload=96 " )'
        % (UPDSINK_PORT_NUM, args.codec)
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-test", factory)

    print(
        "\n *** DeepStream: Launched RTSP Streaming at "
        "rtsp://localhost:%d/ds-test ***\n\n"
        % RTSP_PORT_NUM
    )

    # start play back and listen to events
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)

    for i in range(len(args.input)):
        GObject.timeout_add_seconds(i + 1, add_source, args.input[i])

    try:
        loop.run()
    except BaseException:
        pass

    # cleanup
    pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':
    sys.exit(main())
