curl -X POST -F device_id=1-1-1 -F rtsp_url=rtsp://localhost:8550/stream0 -F grpc_address=10.11.13.49:50051 http://127.0.0.1:19878/add_source
curl -X POST -F device_id=1-1-2 -F rtsp_url=rtsp://localhost:8550/stream1 -F grpc_address=10.11.13.49:50051 http://127.0.0.1:19878/add_source
