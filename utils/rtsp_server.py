#!/usr/bin/env python

import sys
import gi

sys.path.append("../")  # noqa: E402
gi.require_version('Gst', '1.0')  # noqa: E402
gi.require_version('GstRtspServer', '1.0')  # noqa: E402

from gi.repository import Gst, GstRtspServer, GObject, GLib

loop = GLib.MainLoop()
Gst.init(None)


class TestRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, movie_path):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.movie_path = movie_path

    def do_create_element(self, url):
        # set mp4 file path to filesrc's location property
        src_demux = "filesrc location=" + self.movie_path + " ! qtdemux name=demux"
        h264_transcode = "demux.video_0"
        # uncomment following line if video transcoding is necessary
        # h264_transcode = "demux.video_0 ! decodebin ! queue ! x264enc"
        pipeline = "{0} {1} ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(
            src_demux, h264_transcode)
        print("Element created: " + pipeline)
        return Gst.parse_launch(pipeline)


class GstreamerRtspServer:
    def __init__(self):
        self.rtspServer = GstRtspServer.RTSPServer()
        self.rtspServer.props.service = "8550"

        mount_points = self.rtspServer.get_mount_points()
        movie_list = ["dataset/sample_720p.mp4",
                      "dataset/sample_qHD.mp4"]
        for i in range(len(movie_list)):
            factory = TestRtspMediaFactory(movie_list[i])
            factory.set_shared(True)
            mount_points.add_factory("/stream" + str(i), factory)
        self.rtspServer.attach(None)


if __name__ == '__main__':
    s = GstreamerRtspServer()
    loop.run()
