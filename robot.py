import os
import time
import random
import subprocess
from threading import Thread

import cv2
import numpy as np

from arduino_car import Car
from rpi.camera import Camera
from rpi.led import Led
from rpi.ultrasonic_sensor import Ultrasonic
from vision_module import detect
from vision_module import find_template


class Robot:
    SAFE_AREA = 50

    def __init__(self):
        self.car = Car()

        self.cap = Camera().start()
        self.us_left = Ultrasonic(10, 9)
        self.us_right = Ultrasonic(2, 3)

        self.detected = False

        self.target_pos = None
        self.frame = None

        time.sleep(2.0)

        Thread(target=self.update_drive, args=()).start()
        Thread(target=self.update_detect, args=()).start()
        Thread(target=self.audio, args=()).start()

    def update_drive(self):
        while True:
            if self.detected:
                print("tracing...")
                time.sleep(0.8)  # car의 update에서 마지막 이동 신호를 보내도록 함: 이후에 정지
                self.car.move(Car.STOP)
                time.sleep(1.0)  # 충분히 프레임을 업데이트 하여 선명한 정지 화상을 얻도록 함
                self.track(self.target_pos, self.frame)
                self.detected = False
            else:
                print("auto_driving...")
                self.auto_drive()

    def update_detect(self):
        while True:
            if not self.detected:
                print("[detect] nothing detected.")
                self.frame = self.cap.read()
                self.detected, self.target_pos = detect(self.frame)
            else:
                print("[detect] something has found!")

    def auto_drive(self):
        left, right = self.us_left.read(), self.us_right.read()

        start_time = time.time()
        while left < Robot.SAFE_AREA or right < Robot.SAFE_AREA:
            self.car.move(Car.RIGHT if left < right else Car.LEFT)

            if (time.time() - start_time) > 3:
                self.car.move(Car.BACKWARD)
                time.sleep(1.0)
                start_time = time.time()
                self.car.move(Car.RIGHT if left < right else Car.LEFT)
                time.sleep(random.uniform(1.0, 1.8))

            left, right = self.us_left.read(), self.us_right.read()

        self.car.move(Car.FORWARD)

    def audio(self):
        path = "./sounds/"
        file_list = os.listdir(path)
        parms = [path + file for file in file_list]

        while True:
            for parm in parms:
                subprocess.call(["cvlc", "--play-and-exit", parm])

    def track(self, detected_person_pos, full_img):
        x, y, w, h = detected_person_pos

        full_height, full_width, _ = full_img.shape

        target_x, target_y = x + int(w * 0.5), y + int(h * 0.5)
        origin_x, origin_y = int(full_width * 0.5), full_height

        distance_x = target_x - origin_x

        left, right = self.us_left.read(), self.us_right.read()
        img_roi = full_img[y:y + h, x:x + w]

        find_start_time = time.time()
        current_time = time.time() - find_start_time

        while abs(distance_x) > 30 and current_time < 8:
            if distance_x > 0:
                self.car.move(Car.RIGHT)
            else:
                self.car.move(Car.LEFT)

            rotate_time = 0.002 * abs(distance_x)
            print("({}px left: {}sec)".format(abs(distance_x), rotate_time))
            time.sleep(rotate_time)
            self.car.move(Car.STOP)

            img = self.cap.read()
            img_roi, new_pos = find_template(img_roi, img)

            x, y, w, h = new_pos
            target_x = x + int(w * 0.5)
            distance_x = target_x - origin_x

            current_time = time.time() - find_start_time

        self.car.move(Car.FORWARD)
        while left >= Robot.SAFE_AREA and right >= Robot.SAFE_AREA:
            left, right = self.us_left.read(), self.us_right.read()

        self.car.move(Car.STOP)


if __name__ == "__main__":
    robot = Robot()
