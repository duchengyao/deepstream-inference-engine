# Tianshu Inference Engine Docker

## 0x01 Dependencies

### 1.1 Deepstream

> 请参考 [Deepstream User Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html).

**以下实现针对 Tesla V100s 服务器，确保宿主机满足 NVIDIA driver 470.63.01 或更高，需要宿主机 root 权限.**

### 1.2 Docker
**a. 从 Dockerfile 创建镜像**
```
# 在当前路径下执行
docker build -t your-image-name:image-tag.
```
**b. 启动并进入容器**
```
docker run -itd --gpus all --name your-container-name -v /your/path-to/tsif/:/tsif --net host your-image-name:your-image-tag
docker exec -it your-container-name bash

```
## 0x02 Quickstart
> 拉取官方样例进行测试 [Deepstream Python apps](https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git)

### 2.1 一键拉取并完成 python binding
```
bash ./test-sample
```
### 2.2 启动样例 rtsp 服务
```
cd deepstream_python_apps/apps/deepstream-rtsp-in-rtsp-out
python3 deepstream_test1_rtsp_in_rtsp_out.py -i rtsp://xxxx
```
### 2.3 本地查看
* 使用 VLC 或 ffmpeg 通过网络串流展示.
