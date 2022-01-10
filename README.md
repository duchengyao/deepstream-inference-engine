# Tianshu Inference Engine

## 0x01 Dependencies

### 1.1 Deepstream

> 请参考 [Deepstream User Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html)
> 安装最新版的 deepstream 。

需严格按版本号安装，或拉取 DeepStream 的 docker 镜像。

* Ubuntu 18.04 (20.04 也支持，但未经官方测试)
* GStreamer 1.14.5
* NVIDIA driver R470.63.01+
* CUDA 11.4
* cuDNN 8.2+
* TensorRT 8.0.1
* DeepStream SDK 6.0

### 1.2 YOLO v5

* [ultralytics/yolov5](https://github.com/ultralytics/yolov5)

### 1.3 GstRtspServer and introspection typelib

apt-get 安装以下包 ，使用系统的 python 执行，不要尝试用 anaconda 或 pip 安装。

* python3-gi 
* python3-dev
* python3-gst-1.0 
* libgstrtspserver-1.0-0
* gstreamer1.0-rtsp
* python3-gi
* python3-dev
* python3-gst-1.0
* libgirepository1.0-dev
* gobject-introspection 
* gir1.2-gst-rtsp-server-1.0

## 0x02 Quickstart

* 使用 gen_wts_yoloV5.py 将 `pt` 转换为 `wts` & `cfg` 文件 `python3 gen_wts_yoloV5.py -w yolov5n.pt`
* 编译 `CUDA_VER=11.4 make -C nvdsinfer_custom_impl_Yolo`
* 生成 engine & 观看样例: `cd config/official-yolov5n` && `deepstream-app -c deepstream_app_config.txt`
* RTSP in RTSP out: `cd utlis` && `python3 deepstream_rtsp_in_rtsp_out.py -i rtsp://xxxxx`
