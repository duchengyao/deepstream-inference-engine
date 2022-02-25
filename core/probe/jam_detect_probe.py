import numpy as np
import cv2

from common.draw_bounding_boxes import draw_bounding_boxes
from core.probe.probe_base import ProbeBase


class JamDetectProbe(ProbeBase):
    def __init__(self):
        super(JamDetectProbe, self).__init__(
            "configs/official-yolov5n/config_infer_primary_yoloV5.txt")

        # target_id
        self.pgie_class_id_car = 2
        self.pgie_class_id_bus = 5
        self.pgie_class_id_truck = 7

        self.obj_counter = {
            self.pgie_class_id_car: 0,
            self.pgie_class_id_bus: 0,
            self.pgie_class_id_truck: 0
        }

    def frame_postprocess(self, frame_meta, object_list):
        frame_image = frame_meta["image"]
        if frame_meta["frame_num"] % 30 == 0:
            for obj in object_list:
                if obj.class_id in [2, 5, 7]:
                    # convert python array into numpy array format.
                    frame_image = draw_bounding_boxes(frame_image,
                                                      obj.rect_params,
                                                      obj.class_id, obj.confidence,
                                                      None)
                    # covert the array into cv2 default color format
                    self.obj_counter[obj.class_id] += 1

        # send a frame by grpc
        if sum(self.obj_counter.values()) > 10:
            frame_image = cv2.cvtColor(frame_image, cv2.COLOR_RGBA2BGR)
            self.send_msg(frame_image)

        if frame_meta["frame_num"] % 30 == 0:
            print("Frame Number=", frame_meta["frame_num"],
                  "pad_index=", frame_meta["pad_index"],
                  "source_id=", frame_meta["source_id"],
                  "Number of vehicles=", sum(self.obj_counter.values()),
                  "Number of cars=", self.obj_counter[self.pgie_class_id_car],
                  "Number of buses=", self.obj_counter[self.pgie_class_id_bus],
                  "Number of trucks=", self.obj_counter[self.pgie_class_id_truck])
