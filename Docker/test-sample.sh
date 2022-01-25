#!/bin/bash
set -aux
export GIT_SSL_NO_VERIFY=1


git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git
cd deepstream_python_apps
git submodule update --init
cd 3rdparty/gst-python/
./autogen.sh
make
make install

cd ../../bindings
mkdir build
cd build
cmake ..
make -j$(nproc)

pip3 install ./pyds-1.1.0-py3-none*.whl
