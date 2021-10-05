import time

import RPi.GPIO as GPIO

# 파이썬 GPIO 모드
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Ultrasonic:

    MAX_DISTANCE_CM = 300
    MAX_DURATION_TIMEOUT = MAX_DISTANCE_CM * 2 * 29.1  # 17460 # 17460us = 300cm

    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        GPIO.setup(trig_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

        # HC-SR04 시작 전 잠시 대기
        GPIO.output(self.trig_pin, False)
        time.sleep(1)  # 1초


    # cm 환산 함수
    # 아두이노 UltraDistSensor 코드에서 가져옴
    @staticmethod
    def _distanceInCm(duration):
        # 물체에 도착후 돌아오는 시간 계산
        # 시간 = cm / 음속 * 왕복
        # t   = 0.01/340 * 2= 0.000058824초 (58.824us)
    
        # 인식까지의 시간
        # t = 0.01/340 = 0.000029412초 (29.412us)
    
        # duration은 왕복 시간이니 인식까지의 시간에서 2로 나눔
        return (duration / 2) / 29.1


    def read(self):
        # 171206 중간에 통신 안되는 문제 개선용
        fail = False
        time.sleep(0.1)
        # 트리거를 10us 동안 High 했다가 Low로 함.
        # sleep 0.00001 = 10us
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)
    
        pulse_start = 0
        pulse_end = 0
    
        # echo로 신호가 들어 올때까지 대기
        timeout = time.time()
        while GPIO.input(self.echo_pin) == 0:
            # 들어왔으면 시작 시간을 변수에 저장
            pulse_start = time.time()
            if ((pulse_start - timeout) * 1000000) >= Ultrasonic.MAX_DURATION_TIMEOUT:
                # 171206 중간에 통신 안되는 문제 개선용
                # continue
                fail = True
                break
    
            # 171206 중간에 통신 안되는 문제 개선용
            if fail:
                continue
    
        # echo로 인식 종료 시점까지 대기
        timeout = time.time()
        while GPIO.input(self.echo_pin) == 1:
            # 종료 시간 변수에 저장
            pulse_end = time.time()
            if ((pulse_end - pulse_start) * 1000000) >= Ultrasonic.MAX_DURATION_TIMEOUT:
                fail = True
                break
    
            # 171206 중간에 통신 안되는 문제 개선용
            if fail:
                continue
    
        # 인식 시작부터 종료까지의 차가 바로 거리 인식 시간
        pulse_duration = (pulse_end - pulse_start) * 1000000
    
        # 시간을 cm로 환산
        distance = Ultrasonic._distanceInCm(pulse_duration)
        # print(pulse_duration)
        # print('')
        # 자리수 반올림
        distance = round(distance, 2)
    
        # 표시
        return distance
