import base64
import cv2
import grpc
import time


class GrpcClient:
    def __init__(self, address):
        import configs.grpc.inference_result_pb2 as bp2
        import configs.grpc.inference_result_pb2_grpc as pb2_grpc

        channel = grpc.insecure_channel(address)
        self.stub = pb2_grpc.InferenceCheckpointServiceStub(channel)
        self.request = bp2.InferencePhoneDetectionCheckpointRequest

    def send_image(self, frame_image,
                   code="1",
                   detail="{ \"position\": [1,2,3,4] }",
                   result="检测到有人打电话",
                   timestamp=int(time.time())):
        _, buffer_img = cv2.imencode('.jpg', frame_image)
        img_b64 = base64.b64encode(buffer_img).decode('utf-8')
        request_curr = self.request(
            code=code,
            img=img_b64,
            result=result,
            detail=detail,
            time=timestamp)

        response = self.stub.phoneDetectionCheckpoint(request_curr)
        print("Get grpc response ", response)
        return response


if __name__ == '__main__':
    import sys
    import numpy as np

    sys.path.append("../")

    grpc_client = GrpcClient('10.5.24.131:50051')

    img = np.zeros((1024, 768, 3))
    resp = grpc_client.send_image(img)
