import numpy as np
import cv2

import pyds

from gi.repository import Gst

from common.draw_bounding_boxes import draw_bounding_boxes
from common.grpc_client import GrpcClient
from configs import global_config
from core.probe.probe_base import ProbeBase


class JamDetectProbe(ProbeBase):
    def __init__(self):
        self.config_dir = "configs/official-yolov5n/config_infer_primary_yoloV5.txt"
        self.grpc_client = GrpcClient(global_config.GRPC_ADDRESS)

        self.pgie_class_id_car = 2
        self.pgie_class_id_bus = 5
        self.pgie_class_id_truck = 7

    def tiler_src_pad_buffer_probe(self, pad, info, u_data):
        """
        tiler_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
        and update params for drawing rectangle, object information etc.
        """

        gst_buffer = info.get_buffer()
        if not gst_buffer:
            print("Unable to get GstBuffer ")
            return

        # Retrieve batch metadata from the gst_buffer
        # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))

        l_frame = batch_meta.frame_meta_list

        while l_frame is not None:
            try:
                # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
                # The casting is done by pyds.NvDsFrameMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone.
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break

            frame_number = frame_meta.frame_num
            l_obj = frame_meta.obj_meta_list
        
            obj_counter = {
                self.pgie_class_id_car: 0,
                self.pgie_class_id_bus: 0,
                self.pgie_class_id_truck: 0,
            }
            while l_obj is not None:
                try:
                    # Casting l_obj.data to pyds.NvDsObjectMeta
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break

                if obj_meta.class_id in [2,5,7] and frame_number % 30 == 0:
                    # Getting Image data using nvbufsurface
                    # the input should be address of buffer and batch_id
                    n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
                    # convert python array into numy array format.
                    n_frame = draw_bounding_boxes(n_frame,
                                                    obj_meta,
                                                    obj_meta.confidence,
                                                    None)
                    frame_copy = np.array(n_frame, copy=True, order='C')
                    # covert the array into cv2 default color format
                    frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_RGBA2BGR)
                    obj_counter[obj_meta.class_id] += 1
                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break
            
            if sum(obj_counter.values()) > 10:
                try:
                    # cv2.imwrite("a.png", frame_copy)
                    self.grpc_client.send_image(frame_copy)
                    print("send image.")

                except Exception as e:
                    print("grpc failed: ", e)

                    


            if frame_number % 30 == 0:
                print("Frame Number=", frame_number,
                      "pad_index=", frame_meta.pad_index,
                      "source_id=", frame_meta.source_id,
                      "Number of vehicles=", sum(obj_counter.values()),
                      "Number of cars=",obj_counter[self.pgie_class_id_car],
                      "Number of buses=",obj_counter[self.pgie_class_id_bus],
                      "Number of trucks=",obj_counter[self.pgie_class_id_truck])

            try:
                l_frame = l_frame.next
            except StopIteration:
                break

        return Gst.PadProbeReturn.OK
