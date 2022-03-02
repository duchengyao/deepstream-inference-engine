import cv2

from common.draw_bounding_boxes import draw_bounding_boxes
from core.probe.probe_base import ProbeBase


class PhoneCallDetectProbe(ProbeBase):
    def __init__(self):
        super(PhoneCallDetectProbe, self).__init__(
            "configs/phone-call-detect/config_infer_primary_yoloV5.txt")

        self.pgie_class_id_person = 0
        self.pgie_class_id_call = 1

        self.obj_counter = {
            self.pgie_class_id_person: 0,
            self.pgie_class_id_call: 0,
        }

    def frame_postprocess(self, frame_meta, object_list):
        frame_image = frame_meta["image"]
        frame_number = frame_meta["frame_num"]
        for obj in object_list:
            if obj.class_id == 1 and frame_number % 30 == 0:
                # Getting Image data using nvbufsurface
                # the input should be address of buffer and batch_id
                # convert python array into numy array format.
                frame_image = draw_bounding_boxes(frame_image,
                                                  obj.rect_params,
                                                  obj.class_id,
                                                  obj.confidence,
                                                  ['正常', '接电话'])
                # covert the array into cv2 default color format
                self.send_msg(frame_image)

                self.obj_counter[obj.class_id] += 1

        if frame_number % 30 == 0:
            print("Frame Number=", frame_number,
                  "pad_index=", frame_meta["pad_index"],
                  "source_id=", frame_meta["source_id"],
                  "Number of Objects=", len(object_list))
