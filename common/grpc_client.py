import sys

sys.path.append("../")  # noqa: E402

import base64
import cv2
import grpc
import time

import configs.grpc.inference_result_pb2 as bp2
import configs.grpc.inference_result_pb2_grpc as pb2_grpc

Request = bp2.InferencePhoneDetectionCheckpointRequest


class GrpcClient:
    def __init__(self):
        channel = grpc.insecure_channel('10.5.24.131:50051')
        self.stub = pb2_grpc.InferenceCheckpointServiceStub(channel)

    def send_image(self, frame_image):
        _, buffer_img = cv2.imencode('.jpg', frame_image)
        img_b64 = base64.b64encode(buffer_img).decode('utf-8')
        request = Request(code='1-1-1',
                          img=img_b64,
                          result="检测到有人打电话",
                          detail="{ \"position\": [1,2,3,4] }",
                          time=int(time.time()))
        response = self.stub.phoneDetectionCheckpoint(request)
        print("Get grpc response ", response)
        return response


if __name__ == '__main__':
    import numpy as np

    grpc_client = GrpcClient()

    img = np.zeros((1024, 768, 3))
    resp = grpc_client.send_image(img)
