# Tianshu Inference Engine

## 0x01 Dependencies

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

> [官方文档](https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/master/bindings) 不能在 ubuntu 20.04 安装，
> 请参考下面修改过的步骤安装 python bindings.

**For Ubuntu - 20.04 [use python-3.8, python-3.6 will not work] :**

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

## 0x02 Build

`CUDA_VER=11.4 make -C thirdparty/nvdsinfer_custom_impl_Yolo`

## 0x03 Quickstart

* RTSP in RTSP out: `cd utlis` && `python3 deepstream_rtsp_in_rtsp_out.py -i rtsp://xxxxx`
