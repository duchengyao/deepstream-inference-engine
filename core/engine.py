import argparse
import math
import pyds
import sys
import time
import _thread as thread

import gi

gi.require_version('Gst', '1.0')  # noqa: E402
gi.require_version('GstRtspServer', '1.0')  # noqa: E402
gi.require_version("GstVideo", "1.0")  # noqa: E402

from gi.repository import GObject, Gst, GstRtspServer, GLib, GstVideo

from core.probe.phone_call_detect_probe import PhoneCallDetectProbe

frame_count = {}
saved_count = {}
frame_call = {}

TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720
MAX_NUM_SOURCES = 10


class Engine:
    def __init__(self,
                 model_name,
                 batch_size=16,
                 codec="H264",
                 gie="nvinfer",
                 updsink_port_num=5400,
                 rtsp_port_num=8554):

        self.source_id_used_list = []
        self.source_bin_dict = {}

        model = self.select_model(model_name)
        GObject.threads_init()
        Gst.init(None)

        self.pipeline, self.loop, self.streammux = self.create_pipeline(
            batch_size,
            4000000,
            codec,
            batch_size,
            "nvinfer",
            model.tiler_src_pad_buffer_probe,
            updsink_port_num,
            model.config_dir
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

    def add_source(self, uri_name, source_id):
        assert source_id not in self.source_bin_dict.keys(), "Source %d is used." % source_id

        print("Creating source_bin ", uri_name, " \n ")
        source_bin = self.create_source_bin(source_id, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")

        self.source_bin_dict[source_id] = source_bin

        self.pipeline.add(source_bin)

        padname = "sink_%u" % source_id
        sinkpad = self.streammux.get_request_pad(padname)
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad = source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)

        # Set state of source bin to playing
        state_return = source_bin.set_state(Gst.State.PLAYING)

        if state_return == Gst.StateChangeReturn.SUCCESS:
            print("STATE CHANGE SUCCESS\n")
            source_id += 1

        elif state_return == Gst.StateChangeReturn.FAILURE:
            print("STATE CHANGE FAILURE\n")

        elif state_return == Gst.StateChangeReturn.ASYNC:
            state_return = source_bin.get_state(Gst.CLOCK_TIME_NONE)
            source_id += 1

        elif state_return == Gst.StateChangeReturn.NO_PREROLL:
            print("STATE CHANGE NO PREROLL\n")

    def cb_newpad(self, decodebin, pad, data):
        print("In cb_newpad\n")
        caps = pad.get_current_caps()
        gststruct = caps.get_structure(0)
        gstname = gststruct.get_name()
        source_bin = data
        features = caps.get_features(0)

        # Need to check if the pad created by the decodebin is for video and not
        # audio.
        print("gstname=", gstname)
        if gstname.find("video") != -1:
            # Link the decodebin pad only if decodebin has picked nvidia
            # decoder plugin nvdec_*. We do this by checking if the pad caps contain
            # NVMM memory features.
            print("features=", features)
            if features.contains("memory:NVMM"):
                # Get the source bin ghost pad
                bin_ghost_pad = source_bin.get_static_pad("src")
                if not bin_ghost_pad.set_target(pad):
                    sys.stderr.write(
                        "Failed to link decoder src pad to source bin ghost pad\n"
                    )
            else:
                sys.stderr.write(
                    " Error: Decodebin did not pick nvidia decoder plugin.\n")

    def bus_call(self, bus, message, loop):
        t = message.type
        if t == Gst.MessageType.EOS:
            sys.stdout.write("End-of-stream\n")
            loop.quit()
        elif t == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            sys.stderr.write("Warning: %s: %s\n" % (err, debug))
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            sys.stderr.write("Error: %s: %s\n" % (err, debug))
            loop.quit()
        elif t == Gst.MessageType.ELEMENT:
            struct = message.get_structure()
            # Check for stream-eos message
            if struct is not None and struct.has_name("stream-eos"):
                parsed, stream_id = struct.get_uint("stream-id")
                if parsed:
                    # Set eos status of stream to True, to be deleted in delete-sources
                    print("Got EOS from stream %d" % stream_id)
        return True

    def cleanup(self):
        self.pipeline.set_state(Gst.State.NULL)

    def create_pipeline(self,
                        batch_size,
                        bitrate,
                        codec,
                        number_sources,
                        gie,
                        probe,
                        updsink_port_num,
                        config_file_path):
        # Create gstreamer elements */
        # Create Pipeline element that will form a connection of other elements
        print("Creating Pipeline \n ")
        pipeline = Gst.Pipeline()
        is_live = False

        if not pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")
        print("Creating streamux \n ")

        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")

        pipeline.add(streammux)

        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batch-size", batch_size)
        streammux.set_property("batched-push-timeout", 25000)
        streammux.set_property("live-source", 1)

        print("Creating Pgie \n ")
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            sys.stderr.write(" Unable to create pgie \n")
        print("Creating tiler \n ")
        tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
        if not tiler:
            sys.stderr.write(" Unable to create tiler \n")
        print("Creating nvvidconv \n ")
        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
        if not nvvidconv:
            sys.stderr.write(" Unable to create nvvidconv \n")
        print("Creating nvosd \n ")
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")
        nvvidconv_postosd = Gst.ElementFactory.make(
            "nvvideoconvert", "convertor_postosd")
        if not nvvidconv_postosd:
            sys.stderr.write(" Unable to create nvvidconv_postosd \n")

        # Create a caps filter
        caps = Gst.ElementFactory.make("capsfilter", "filter")
        caps.set_property(
            "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
        )

        # Make the encoder
        if codec == "H264":
            encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
            print("Creating H264 Encoder")
        elif codec == "H265":
            encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
            print("Creating H265 Encoder")
        else:
            encoder = None

        if not encoder:
            sys.stderr.write(" Unable to create encoder")
        encoder.set_property("bitrate", bitrate)

        # Make the payload-encode video into RTP packets
        if codec == "H264":
            rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
            print("Creating H264 rtppay")
        elif codec == "H265":
            rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
            print("Creating H265 rtppay")
        else:
            rtppay = None
        if not rtppay:
            sys.stderr.write(" Unable to create rtppay")

        # Make the UDP sink
        sink = Gst.ElementFactory.make("udpsink", "udpsink")
        if not sink:
            sys.stderr.write(" Unable to create udpsink")

        sink.set_property("host", "224.224.255.255")
        sink.set_property("port", updsink_port_num)
        sink.set_property("async", False)
        sink.set_property("sync", 1)
        sink.set_property("qos", 0)

        pgie.set_property("config-file-path", config_file_path)
        pgie_batch_size = pgie.get_property("batch-size")

        if pgie_batch_size != batch_size:
            print(
                "WARNING: Overriding infer-config batch-size", pgie_batch_size,
                " with number of sources ", batch_size, " \n",
            )
            pgie.set_property("batch-size", batch_size)

        # Use CUDA unified memory in the pipeline so frames
        # can be easily accessed on CPU in Python.
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        streammux.set_property("nvbuf-memory-type", mem_type)
        nvvidconv.set_property("nvbuf-memory-type", mem_type)
        tiler.set_property("nvbuf-memory-type", mem_type)

        print("Adding elements to Pipeline \n")
        tiler_rows = 4  # int(math.sqrt(number_sources))
        tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
        tiler.set_property("rows", tiler_rows)
        tiler.set_property("columns", tiler_columns)
        tiler.set_property("width", TILED_OUTPUT_WIDTH)
        tiler.set_property("height", TILED_OUTPUT_HEIGHT)

        pipeline.add(pgie)
        pipeline.add(tiler)
        pipeline.add(nvvidconv)
        pipeline.add(nvosd)
        pipeline.add(nvvidconv_postosd)
        pipeline.add(caps)
        pipeline.add(encoder)
        pipeline.add(rtppay)
        pipeline.add(sink)

        streammux.link(pgie)
        pgie.link(nvvidconv)
        nvvidconv.link(tiler)
        tiler.link(nvosd)
        nvosd.link(nvvidconv_postosd)
        nvvidconv_postosd.link(caps)
        caps.link(encoder)
        encoder.link(rtppay)
        rtppay.link(sink)

        # create an event loop and feed gstreamer bus mesages to it
        loop = GObject.MainLoop()
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call, loop)

        sys.stderr.write("pipeline.set_state(Gst.State.PAUSED)\n")
        pipeline.set_state(Gst.State.PAUSED)

        tiler_sink_pad = tiler.get_static_pad("sink")
        if not tiler_sink_pad:
            sys.stderr.write(" Unable to get src pad \n")
        else:
            tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, probe, 0)

        return pipeline, loop, streammux

    def create_source_bin(self, index, uri):
        print("Creating source bin")

        # Create a source GstBin to abstract this bin's content from the rest of the
        # pipeline
        bin_name = "source-bin-%02d" % index
        print(bin_name)
        nbin = Gst.Bin.new(bin_name)
        if not nbin:
            sys.stderr.write(" Unable to create source bin \n")

        # Source element for reading from the uri.
        # We will use decodebin and let it figure out the container format of the
        # stream and the codec and plug the appropriate demux and decode plugins.
        uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
        if not uri_decode_bin:
            sys.stderr.write(" Unable to create uri decode bin \n")
        # We set the input uri to the source element
        uri_decode_bin.set_property("uri", uri)
        # Connect to the "pad-added" signal of the decodebin which generates a
        # callback once a new pad for raw data has beed created by the decodebin
        uri_decode_bin.connect("pad-added", self.cb_newpad, nbin)
        uri_decode_bin.connect("child-added", self.decodebin_child_added, nbin)

        # We need to create a ghost pad for the source bin which will act as a proxy
        # for the video decoder src pad. The ghost pad will not have a target right
        # now. Once the decode bin creates the video decoder and generates the
        # cb_newpad callback, we will set the ghost pad target to the video decoder
        # src pad.
        Gst.Bin.add(nbin, uri_decode_bin)
        bin_pad = nbin.add_pad(
            Gst.GhostPad.new_no_target(
                "src", Gst.PadDirection.SRC))
        if not bin_pad:
            sys.stderr.write(" Failed to add ghost pad in source bin \n")
            return None
        return nbin

    def decodebin_child_added(self, child_proxy, Object, name, user_data):
        print("Decodebin child added:", name, "\n")
        if name.find("decodebin") != -1:
            Object.connect("child-added", self.decodebin_child_added, user_data)
        if name.find("nvv4l2decoder") != -1:
            Object.set_property("gpu_id", 0)  # TODO: GPU_ID=0

    def remove_source(self, source_id):
        assert source_id in self.source_bin_dict.keys(), "Source %d not found." % source_id

        # Attempt to change status of source to be released
        state_return = self.source_bin_dict[source_id].set_state(Gst.State.NULL)

        if state_return == Gst.StateChangeReturn.SUCCESS:
            print("STATE CHANGE SUCCESS\n")
            pad_name = "sink_%u" % source_id
            print(pad_name)
            # Retrieve sink pad to be released
            sinkpad = self.streammux.get_static_pad(pad_name)
            # Send flush stop event to the sink pad, then release from the streammux
            sinkpad.send_event(Gst.Event.new_flush_stop(False))
            self.streammux.release_request_pad(sinkpad)
            print("STATE CHANGE SUCCESS\n")
            # Remove the source bin from the pipeline
            self.pipeline.remove(self.source_bin_dict[source_id])

        elif state_return == Gst.StateChangeReturn.FAILURE:
            print("STATE CHANGE FAILURE\n")

        elif state_return == Gst.StateChangeReturn.ASYNC:
            state_return = self.source_bin_dict[source_id].get_state(Gst.CLOCK_TIME_NONE)
            pad_name = "sink_%u" % source_id
            print(pad_name)
            sinkpad = self.streammux.get_static_pad(pad_name)
            sinkpad.send_event(Gst.Event.new_flush_stop(False))
            self.streammux.release_request_pad(sinkpad)
            print("STATE CHANGE ASYNC\n")
            self.pipeline.remove(self.source_bin_dict[source_id])

        self.source_bin_dict.pop(source_id)

    def select_model(self, model_name):
        if model_name == "phone_call_detect":
            return PhoneCallDetectProbe()
        else:
            assert False

    def start(self):
        try:
            thread.start_new_thread(self.loop.run, ())
        except Exception as e:
            # TODO: log Fatal
            print(e)
