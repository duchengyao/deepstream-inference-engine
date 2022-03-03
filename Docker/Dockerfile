# 拉取对应的 deepstream-devel 镜像
FROM nvcr.io/nvidia/deepstream:6.0-devel
# 更新源
RUN apt update
# 安装依赖
RUN apt install -y git python-dev python3 python3-pip python3.6-dev python3.8-dev cmake g++ build-essential \
    libglib2.0-dev libglib2.0-dev-bin python-gi-dev libtool m4 autoconf automake libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev gir1.2-gst-rtsp-server-1.0
# 更新 pip
RUN pip3 install --upgrade pip
# 安装依赖 module
RUN python3 -m pip install Flask PyYAML grpcio grpcio-tools -i https://pypi.tuna.tsinghua.edu.cn/simple/
