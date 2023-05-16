# Inference Engine Docker

## 0x01 Dependencies

### 1.1 Deepstream

> 请参考 [Deepstream User Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html).

**以下实现针对 Tesla V100s 服务器，确保宿主机满足 NVIDIA driver 470.63.01 或更高，需要宿主机 root 权限.**

### 1.2 Docker
**a. 从 Dockerfile 创建镜像**
```
# 在当前路径下执行
docker build -t your-image-name:image-tag .
```
**b. 启动并进入容器**
```
docker run -itd --gpus all --name your-container-name -v /your/path-to/tsif/:/tsif/ --net host your-image-name:your-image-tag
docker exec -it your-container-name bash

```
**c. 一键拉取并完成 python binding**
> 参考官方样例 [Deepstream Python apps](https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git)
```
cd /tsif
bash ./test-sample.sh
```
**完成以上步骤后，可以通过以下 Quickstart 运行 nvidia 官方测试样例进行测试，或者直接参考主目录 Readme，从 1.3 YOLO v5 继续执行跑通 tsif**

## 0x02 Quickstart
### 2.1 启动样例 rtsp 服务
```
cd /opt/nvidia/deepstream/deepstream-6.0/samples/deepstream_python_apps/apps/deepstream-rtsp-in-rtsp-out
python3 deepstream_test1_rtsp_in_rtsp_out.py -i rtsp://xxxx
```
### 2.2 本地查看
* 使用 VLC 或 ffmpeg 通过网络串流展示.


## 0x03 ToubleShooting
1. `CAfile: /etc/ssl/certs/ca-certificates.crt CRLfile: none`
* 解决方法：`export GIT_SSL_NO_VERIFY=1`
2. `No package 'gstreamer-1.0' found`
* 解决方法：`apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev`
3. `ValueError: Namespace GstRtspServer not available`
* 解决方法：`apt-get install gir1.2-gst-rtsp-server-1.0`
4. `ERROR: ...... failed because file path: ...... open error`
* 解决方法：确保报错路径中包含所需文件（首次尝试 Quickstart 建议拷贝  `test-sample.sh` 至 `/opt/nvidia/deepstream/deepstream-6.0/samples/` 并在该路径下执行后续操作）
