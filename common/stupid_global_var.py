global device2source, source2device
device2source = {}
source2device = {}


def update_device_dict():
    source2device.clear()
    for k, v in device2source.items():
        source2device[v] = k
    print("device_dict updated. ", source2device)
