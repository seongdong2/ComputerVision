import RPi.GPIO as GPIO

# 파이썬 GPIO 모드
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Led:

    def __init__(self, led_pin):
        self.led_pin = led_pin
        GPIO.setup(self.led_pin, GPIO.OUT)
        self.off()

    def __del__(self):
        self.off()

    def on(self):
        GPIO.output(self.led_pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.led_pin, GPIO.LOW)

if __name__ == "__main__":
    Led(5)