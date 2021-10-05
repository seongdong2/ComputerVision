import serial


class Car:
    FORWARD = "1"
    BACKWARD = "2"
    RIGHT = "3"
    LEFT = "4"
    STOP = "5"

    def __init__(self):
        self.s = serial.Serial("/dev/ttyACM0", 9600)

    def __del__(self):
        self.s.close()

    def move(self, move_type):
        """
        :param move_type: Car.FORWARD, Car.LEFT 와 같은 움직임 유형
        이전 명령이 남아있다면 다 보낼 때까지 대기한 다음
        움직임 값을 시리얼 통신을 이용해 아두이노로 전송한다.
        """
        if self.s.isOpen():
            self.s.flush()
            self.s.write(move_type.encode())

