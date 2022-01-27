import cv2


def draw_bounding_boxes(image, obj_meta, confidence, pgie_classes_str):
    confidence = '{0:.2f}'.format(confidence)
    rect_params = obj_meta.rect_params
    top = int(rect_params.top)
    left = int(rect_params.left)
    width = int(rect_params.width)
    height = int(rect_params.height)
    obj_name = pgie_classes_str[obj_meta.class_id]

    color = (0, 0, 255, 0)
    image = cv2.rectangle(image,
                          (left, top),
                          (left + width, top + height),
                          color,
                          2,
                          cv2.LINE_4)

    # Note that on some systems cv2.putText erroneously draws horizontal lines across the image
    image = cv2.putText(image,
                        obj_name + ',C=' + str(confidence),
                        (left - 10, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2)
    return image
