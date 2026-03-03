import threading
import zmq
import cv2
import struct
import time
import numpy as np
from pymurapi import api


class Simulator(api.MurApiBase, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        api.MurApiBase.__init__(self)

        ctx = zmq.Context()
        self.unpacker = struct.Struct('=7f3B3H')
        self.packer = struct.Struct('=b8h3B2f')
        self.front_socket = ctx.socket(zmq.SUB)
        self.bottom_socket = ctx.socket(zmq.SUB)
        self.mcu_socket = ctx.socket(zmq.SUB)
        self.motors_socket = ctx.socket(zmq.PAIR)
        self.front_image = np.zeros((240, 320, 3), np.uint8)
        self.bottom_image = np.zeros((240, 320, 3), np.uint8)
        self.colorRGB = [0, 0, 0]
        self.hydrophone_signals_tr = [0]
        self.hydrophone_signals_tl = [0]
        self.hydrophone_signals_fr = [0]
        self.hydrophone_distances_tr = [0]
        self.hydrophone_distances_tl = [0]
        self.hydrophone_distances_fr = [0]


    def get_image_front(self):
        return self.front_image

    def open_grabber(self):
        self.colorRGB[0] = 1

    def close_grabber(self):
        self.colorRGB[0] = 0

    def shoot(self):
        self.colorRGB[1] += 2
        if self.colorRGB[1] > 100:
            self.colorRGB[1] = 1

    def drop(self):
        self.colorRGB[2] += 2
        if self.colorRGB[2] > 100:
            self.colorRGB[2] = 1

    def get_hydrophone_signal(self):
        return self.hydrophone_signals_tr[0], self.hydrophone_signals_tl[0], self.hydrophone_signals_fr[0], \
        self.hydrophone_distances_tr[0] / 100, self.hydrophone_distances_tl[0] / 100, self.hydrophone_distances_fr[0] / 100
        
    def get_image_bottom(self):
        return self.bottom_image

    def run(self):
        while True:
            self._update()
            time.sleep(0.020)

    def prepare(self):
        bottom_image_url = "tcp://127.0.0.1:1771"
        front_image_url = "tcp://127.0.0.1:1772"
        mcu_url = "tcp://127.0.0.1:3390"
        motors_url = "tcp://127.0.0.1:3391"

        self.front_socket.connect(front_image_url)
        self.front_socket.setsockopt(zmq.LINGER, 0)
        self.front_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.bottom_socket.connect(bottom_image_url)
        self.bottom_socket.setsockopt(zmq.LINGER, 0)
        self.bottom_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.mcu_socket.connect(mcu_url)
        self.mcu_socket.setsockopt(zmq.LINGER, 0)
        self.mcu_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.motors_socket.connect(motors_url)
        self.motors_socket.setsockopt(zmq.SNDTIMEO, 3000)

        self.start()

    def _update(self):
        front_image_jpg = np.fromstring(self.front_socket.recv(), dtype='uint8')
        bottom_image_jpg = np.fromstring(self.bottom_socket.recv(), dtype='uint8')

        data = self.mcu_socket.recv()

        self.yaw, \
        self.pitch, \
        self.roll, \
        self.depth, \
        self.temperature, \
        self.pressure, \
        self.voltage, \
        self.hydrophone_signals_tr[0], \
        self.hydrophone_signals_tl[0], \
        self.hydrophone_signals_fr[0], \
        self.hydrophone_distances_tr[0], \
        self.hydrophone_distances_tl[0], \
        self.hydrophone_distances_fr[0] = self.unpacker.unpack(data)

        message = self.packer.pack(self.is_thrust_in_ms,
                                   self.motors_power[0],
                                   self.motors_power[1],
                                   self.motors_power[2],
                                   self.motors_power[3],
                                   self.motors_power[4],
                                   self.motors_power[5],
                                   self.motors_power[6],
                                   self.motors_power[7],
                                   self.colorRGB[0],
                                   self.colorRGB[1],
                                   self.colorRGB[2],
                                   self.on_delay,
                                   self.off_delay)
        self.motors_socket.send(message)

        self.front_image = cv2.imdecode(front_image_jpg, 1)
        self.bottom_image = cv2.imdecode(bottom_image_jpg, 1)
