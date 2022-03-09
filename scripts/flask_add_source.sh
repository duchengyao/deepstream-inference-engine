curl -X POST -F device_id=aaa -F rtsp_url=rtsp://localhost:8550/stream0 -F grpc_address=10.5.24.131:50051 http://127.0.0.1:19878/add_source
curl -X POST -F device_id=bbb -F rtsp_url=rtsp://localhost:8550/stream1 -F grpc_address=10.5.24.131:50051 http://127.0.0.1:19878/add_source
