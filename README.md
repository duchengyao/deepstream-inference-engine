# Inference Engine

基于 Deepstream 的深度学习多路视频推理平台。

## 0x01 Dependencies

* [Triton](https://developer.nvidia.com/nvidia-triton-inference-server) 是 NVIDIA 推出的 Inference Server，提供 AI
  模型的部署服务。客户端可以使用 HTTP/REST 或 gRPC 的方式来请求服务。支持各种深度学习后端，支持 k8s，和多种批处理算法。

* [Deepstream](https://developer.nvidia.com/deepstream-sdk) 是 NVIDIA 开发的 SDK，适合快速开发和部署音/视频 AI 应用程序和服务。 
  提供多平台、高扩展性，支持 TLS 安全加密，可以部署在本地、边缘和云端。 参考样例可以查看 SDK
  和 [NVIDIA IOT GitHub](https://github.com/orgs/NVIDIA-AI-IOT/repositories?q=deepstream) .

* [GStreamer](https://gstreamer.freedesktop.org/) 是用来构建流媒体应用的开源多媒体框架，其目标是要简化音/视频应用程序的开发。 
  GStreamer 为 GNOME 桌面环境下 和 webkit 的多媒体框架，是 linux 官方推荐的流媒体框架，基于 GPL 协议。

### 1.1 Deepstream

> 请参考 [Deepstream User Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html)
> 安装最新版的 deepstream.

需严格按版本号安装，或拉取 DeepStream 的 docker 镜像。

* Ubuntu 18.04 (20.04 也支持，但未经官方测试)
* CUDA 11.4 latest
* NVIDIA driver （CUDA deb 自带）
* TensorRT latest
* cuDNN (tensorrt 自带)
* DeepStream SDK 6.0

### 1.2 Deepstream python bindings

#### 1.2.1 For Ubuntu - 18.04 :

参考 [官方文档](https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/master/bindings).

#### 1.2.2 For Ubuntu - 20.04 [use python-3.8, python-3.6 will not work] :

官方文档在 ubuntu 20.04 的安装方法错误， 请参考下面的步骤安装 python bindings.

**a. Base dependencies**

```
apt install python3-gi python3-dev python3-gst-1.0 python-gi-dev git python-dev \
    python3 python3-pip python3.8-dev cmake g++ build-essential libglib2.0-dev \
    libglib2.0-dev-bin python-gi-dev libtool m4 autoconf automake

export GST_LIBS="-lgstreamer-1.0 -lgobject-2.0 -lglib-2.0"
export GST_CFLAGS="-pthread -I/usr/include/gstreamer-1.0 -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include"
```

**b. Initialization of submodules**

```
git submodule update --init
```

**c. Installing Gst-python**

```
cd 3rdparty/gst-python/
# 修改 acinclude.m4 L:82 的 PYTHON_LIBS=`$PYTHON-config --ldflags 2>/dev/null`
# 为 PYTHON_LIBS=`$PYTHON-config --libs --embed 2>/dev/null` || PYTHON_LIBS=`$PYTHON-config --libs 2>/dev/null`
# 参考 https://gitlab.freedesktop.org/gstreamer/gst-python/-/merge_requests/14/diffs
./autogen.sh PYTHON=python3.8
make
sudo make install
```

**d. Building the bindings**

```
cd deepstream_python_apps/bindings
mkdir build
cd build
cmake ..  -DPYTHON_MAJOR_VERSION=3 -DPYTHON_MINOR_VERSION=8
make
```

**e. Using the generated pip wheel**

```
pip3 install ./pyds-1.1.0-py3-none*.whl
```

### 1.3 YOLO v5

* clone [ultralytics/yolov5](https://github.com/ultralytics/yolov5)
* 将 `utils/gen_wts_yoloV5.py` 复制到 `ultralytics/yolov5`
* 使用 `gen_wts_yoloV5.py` 将 `pt` 转换为 `wts` & `cfg` 文件 `python3 gen_wts_yoloV5.py -w yolov5n.pt`

### 1.4 gRPC

参考 https://grpc.io/docs/languages/python/quickstart/

* `cd configs/grpc`
* `python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inference_result.proto`
* 将 `inference_result_pb2_grpc.py` 第四行改为 `from . import inference_result_pb2 as inference__result__pb2`

## 0x02 Build

`CUDA_VER=11.4 make -C thirdparty/nvdsinfer_custom_impl_Yolo`

## 0x03 Quickstart

> TODO: 重构这段 readme

### 3.1 启动 inference engine

`python3 app.py [phone_call_detect|jam_detect] [-d|--rtsp_port_num=8553|--flask_address=0.0.0.0|flask_port=8554]`

如： `python3 app.py jam_detect --flask_port=8553`
  
### 3.2 添加资源

> 向 inference engine 添加需要推理的rtsp流

向 inference engine 发送 post 请求，默认地址是 http://127.0.0.1:19878/add_source，参数如下：

```
device_id: str, 设备id 
rtsp_url: str, 需要推理的流
address: str, grpc_address (TODO: 改名字）
```

如：

```
curl -X POST \
-F device_id=12 \
-F rtsp_url=http://10.11.12.102:83/openUrl/YioPqRq/live.m3u8 \
-F grpc_address=10.5.24.131:50051 \
http://127.0.0.1:19878/add_source
```

另外，提供了一个角本来添加资源 `bash scripts/flask_add_source.sh`

### 3.3 删除资源

原理跟添加资源相似，可参考 `scripts/flask_remove_source.sh`


### 3.3 展示结果

可以通过 ffplay vlc 等媒体播放器查看实时的推理结果，默认 ip 为 `rtsp://localhost:8554/ds-test`
