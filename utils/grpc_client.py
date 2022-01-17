import sys

sys.path.append("../")

import time

import grpc
import configs.grpc.inference_result_pb2 as bp2
import configs.grpc.inference_result_pb2_grpc as pb2_grpc

Request = bp2.InferencePhoneDetectionCheckpointRequest


class GrpcClient:
    def __init__(self):
        channel = grpc.insecure_channel('10.5.24.131:50051')
        self.stub = pb2_grpc.InferenceCheckpointServiceStub(channel)

    def run(self):
        request = Request(code='1-1-1',
                          result="检测到有人打电话",
                          detail="{ \"position\": [1,2,3,4] }",
                          time=int(time.time()))
        response = self.stub.phoneDetectionCheckpoint(request)
        print("Get grpc response ",response)
        return response


if __name__ == '__main__':
    grpc_client = GrpcClient()
    grpc_client.run()
