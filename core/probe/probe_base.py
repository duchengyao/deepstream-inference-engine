import pyds
import numpy as np

from gi.repository import Gst

from common.grpc_client import GrpcClient
from configs import global_config


class ProbeBase:
    def __init__(self, config_dir) -> None:
        self.config_dir = config_dir
        self.grpc_client = GrpcClient(global_config.GRPC_ADDRESS)

    def tiler_src_pad_buffer_probe(self, pad, info, u_data):
        """
        tiler_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
        and update params for drawing rectangle, object information etc.
        """

        self.gst_buffer = info.get_buffer()
        if not self.gst_buffer:
            print("Unable to get GstBuffer ")
            return

        # Retrieve batch metadata from the gst_buffer
        # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(self.gst_buffer))

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

            l_obj = frame_meta.obj_meta_list

            object_list = []

            # Getting Image data using nvbufsurface
            # the input should be address of buffer and batch_id
            # convert python array into numy array format.
            n_frame = pyds.get_nvds_buf_surface(hash(self.gst_buffer), frame_meta.batch_id)
            frame_image = np.array(n_frame, copy=True, order='C')
            frame_meta_with_image = {"image": frame_image,
                                     "pad_index": frame_meta.pad_index,
                                     "source_id": frame_meta.source_id,
                                     "frame_num": frame_meta.frame_num}
            while l_obj is not None:
                try:
                    # Casting l_obj.data to pyds.NvDsObjectMeta
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                    object_list.append(obj_meta)
                    l_obj = l_obj.next

                except StopIteration:
                    break

            self.frame_postprocess(frame_meta_with_image, object_list)

            try:
                l_frame = l_frame.next
            except StopIteration:
                break

        return Gst.PadProbeReturn.OK

    def frame_postprocess(self, frame_meta, object_list):
        """
        object.class_id
        object.confidence
        object.rect_params
        """
        pass

    def send_msg(self, frame):
        try:
            # cv2.imwrite("a.png", frame_copy)
            self.grpc_client.send_image(frame)
            print("send image.")

        except Exception as e:
            print("grpc failed: ", e)
