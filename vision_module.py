import numpy as np
import cv2

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

net = cv2.dnn.readNetFromCaffe(
    "MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")

BLACK_CRITERIA = 70


def detect(frame):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)

    net.setInput(blob)
    detections = net.forward()

    result_all = []
    result_black = []

    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.3:
            idx = int(detections[0, 0, i, 1])

            if CLASSES[idx] == "person":
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                startX, startY, endX, endY = box.astype("int")
                x, y, w, h = startX, startY, endX - startX, endY - startY

                result_all.append((confidence, (x, y, w, h)))

                cut_size = int(min(w, h) / 6)
                black_value = np.mean(frame[y + cut_size:y + h - cut_size, x + cut_size:x + w - cut_size])

                if black_value < BLACK_CRITERIA:
                    result_black.append((confidence, (x, y, w, h)))

    if result_black:
        result_black.sort(key=lambda x: x[0])
        return True, result_black[-1][1]
    else:
        return False, None


def find_template(template, full_img):
    h, w, _ = template.shape
    full_img_copy = full_img.copy()

    res = cv2.matchTemplate(full_img_copy, template, cv2.TM_CCOEFF)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc

    x = top_left[0]
    y = top_left[1]

    return full_img[y:y + h, x:x + w], (x, y, w, h)