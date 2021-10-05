# import the necessary packages
from imutils import resize

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2

import RPi.GPIO as GPIO

# 파이썬 GPIO 모드
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Camera:
    def __init__(self, resolution=(640, 480), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def __del__(self):
        self.stopped = True

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                break

    def read(self):
        # return the frame most recently read
        img = resize(self.frame, width=400)
        img = cv2.flip(img, -1)
        return img
