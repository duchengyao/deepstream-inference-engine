## gen_wts_yoloV5.py

> 将 yolo 的 pt 转换成 wts 和 cfg，需要配合原始的 yolo 工程使用，
> 代码来自 [DeepStream-Yolo](https://github.com/marcoslucianops/DeepStream-Yolo) 。
> 
> **NOTE**: For YOLOv5 P6 or custom models, check the gen_wts_yoloV5.py args 
> and use them according to your model.

* Input weights (.pt) file path **(required)** `-w or --weights`
* Input cfg (.yaml) file path `-c or --yaml`
* Model width **(default = 640 / 1280 [P6])** `-mw or --width`
* Model height **(default = 640 / 1280 [P6])** `-mh or --height`
* Model channels **(default = 3)** `-mc or --channels`
* P6 model `--p6`

## rtsp_server.py

> 将 mp4 发布成 rtsp 流，供调试使用。

* 视频文件已经包含在项目中，直接执行 `rtsp_server.py` 即可。