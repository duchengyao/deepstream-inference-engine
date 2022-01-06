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

## 0x02 Quickstart

1. 使用 gen_wts_yoloV5.py 将 `pt` 转换为 `wts` / `cfg` 文件。 `python3 gen_wts_yoloV5.py -w yolov5n.pt`
2. 编译 `CUDA_VER=11.4 make -C nvdsinfer_custom_impl_Yolo`
3. 运行 `deepstream-app -c deepstream_app_config.txt`

## 0x03 gen_wts_yoloV5.py

> **NOTE**: For YOLOv5 P6 or custom models, check the gen_wts_yoloV5.py args and use them according to your model

* Input weights (.pt) file path **(required)** `-w or --weights`
* Input cfg (.yaml) file path `-c or --yaml`
* Model width **(default = 640 / 1280 [P6])** `-mw or --width`
* Model height **(default = 640 / 1280 [P6])** `-mh or --height`
* Model channels **(default = 3)** `-mc or --channels`
* P6 model `--p6`


