## gen_wts_yoloV5.py

> **NOTE**: For YOLOv5 P6 or custom models, check the gen_wts_yoloV5.py args and use them according to your model

* Input weights (.pt) file path **(required)** `-w or --weights`
* Input cfg (.yaml) file path `-c or --yaml`
* Model width **(default = 640 / 1280 [P6])** `-mw or --width`
* Model height **(default = 640 / 1280 [P6])** `-mh or --height`
* Model channels **(default = 3)** `-mc or --channels`
* P6 model `--p6`

## deepstream_test1_rtsp_in_rtsp_out.py

```
To get test app usage information:
-----------------------------------
  $ python3 deepstream_test1_rtsp_in_rtsp_out.py -h
  
To run the test app with default settings:
------------------------------------------
  1) NVInfer
      $ python3 deepstream_test1_rtsp_in_rtsp_out.py -i rtsp://sample_1.mp4 rtsp://sample_2.mp4 rtsp://sample_N.mp4  -g nvinfer
  2) NVInferserver
      bash /opt/nvidia/deepstream/deepstream-<Version>/samples/prepare_ds_trtis_model_repo.sh
      $ python3 deepstream_test1_rtsp_in_rtsp_out.py -i rtsp://sample_1.mp4 rtsp://sample_2.mp4 rtsp://sample_N.mp4  -g nvinferserver
  
Default RTSP streaming location:
  rtsp://<server IP>:8554/ds-test

This document shall describe the sample deepstream_test1_rtsp_in_rtsp_out application.

This sample app is derived from the deepstream-test3 and deepStream-test1-rtsp-out

This sample app specifically includes following : 
  - Accepts RTSP stream as input and gives out inference as RTSP stream
  - User can choose NVInfer and NVInferserver as GPU inference engine

  If NVInfer is selected then : 
    For reference, here are the config files used for this sample :
    1. The 4-class detector (referred to as pgie in this sample) uses
        dstest1_pgie_config.txt
    2. This 4 class detector detects "Vehicle , RoadSign, TwoWheeler, Person".


    In this sample, first create one instance of "nvinfer", referred as the pgie.
    This is our 4 class detector and it detects for "Vehicle , RoadSign, TwoWheeler,
    Person".

  If NVInferserver is selected then:
    1. Uses SSD neural network running on Triton Inference Server
    2. Selects custom post-processing in the Triton Inference Server config file
    3. Parses the inference output into bounding boxes
    4. Performs post-processing on the generated boxes with NMS (Non-maximum Suppression)
    5. Adds detected objects into the pipeline metadata for downstream processing
    6. Encodes OSD output and shows visual output over RTSP.

```