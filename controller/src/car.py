import socket
import struct

import cv2


class Car:

    def __init__(self, host, control_port=2001,
                 sensor_port=2002,
                 camera_port=8080,
                 time_out=1):
        # Create addresses
        control_addr = (host, control_port)
        sensor_addr = (host, sensor_port)
        camera_addr = 'http://%s:%d/?action=stream' % (host, camera_port)
        # Connect to control port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.settimeout(time_out)
        self.control_socket.connect(control_addr)
        # Connect to sensor port
        self.sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sensor_socket.settimeout(time_out)
        self.sensor_socket.connect(sensor_addr)
        # Connect to camera stream
        self.camera_stream = cv2.VideoCapture(camera_addr)
        # Create action map
        self.action_map = [self.turn_left, self.turn_right, self.forward]

    def read_camera(self):
        return self.camera_stream.read()

    def read_sensor(self):
        self.sensor_socket.send(b'\xff')
        data = self.sensor_socket.recv(1)
        data = struct.unpack('B', data)[0]
        return (data & 0x1) >> 0, (data & 0x2) >> 1

    def step(self, action):
        assert action in range(0, 3)
        self.action_map[action]()

    def stop(self):
        self.control_socket.send(b'\xff\x00\x00\x00\xff')

    def forward(self):
        self.control_socket.send(b'\xff\x00\x01\x00\xff')

    def backward(self):
        self.control_socket.send(b'\xff\x00\x02\x00\xff')

    def turn_left(self):
        self.control_socket.send(b'\xff\x00\x03\x00\xff')

    def turn_right(self):
        self.control_socket.send(b'\xff\x00\x04\x00\xff')

    def set_speed(self, speed):
        self.set_left_speed(speed)
        self.set_right_speed(speed)

    def set_left_speed(self, speed):
        assert speed <= 100
        self.control_socket.send(b'\xff\x02\x01' + bytes([speed]) + b'\xff')

    def set_right_speed(self, speed):
        assert speed <= 100
        self.control_socket.send(b'\xff\x02\x02' + bytes([speed]) + b'\xff')