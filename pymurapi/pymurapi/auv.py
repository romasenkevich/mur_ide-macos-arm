import threading
import zmq
import struct
import time
from pymurapi import api


class Auv(api.MurApiBase, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        api.MurApiBase.__init__(self)

        ctx = zmq.Context()
        self.telemetry_unpacker = struct.Struct('=7fI')
        self.control_packer = struct.Struct('=b8h3B2f')
        self.telemetry_v2_unpacker = struct.Struct('=4B')
        self.control_v2_packer = struct.Struct('=78B')

        self.telemetry_socket = ctx.socket(zmq.SUB)
        self.control_socket = ctx.socket(zmq.PAIR)
        self.telemetry_v2_socket = ctx.socket(zmq.SUB)
        self.control_v2_socket = ctx.socket(zmq.PAIR)

    def get_image_front(self):
        print("get_image_front function works only in simulator.")
        return

    def get_image_bottom(self):
        print("get_image_bottom function works only in simulator.")
        return

    def run(self):
        while True:
            self._update()
            time.sleep(0.001)

    def prepare(self):
        telemetry_url    = "tcp://127.0.0.1:2001"
        control_url      = "tcp://127.0.0.1:2002"
        telemetry_v2_url = "tcp://127.0.0.1:2003"
        control_v2_url   = "tcp://127.0.0.1:2004"

        self.telemetry_socket.connect(telemetry_url)
        self.telemetry_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.telemetry_socket.setsockopt(zmq.LINGER, 0)

        self.telemetry_v2_socket.connect(telemetry_v2_url)
        self.telemetry_v2_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.telemetry_v2_socket.setsockopt(zmq.LINGER, 0)

        self.control_socket.connect(control_url)
        self.control_socket.setsockopt(zmq.SNDTIMEO, 3000)

        self.control_v2_socket.connect(control_v2_url)
        self.control_v2_socket.setsockopt(zmq.SNDTIMEO, 3000)

        time.sleep(0.1)
        self._update()

        self.start()

    def _update(self):
        self.yaw, self.pitch, self.roll, self.depth, self.temperature, self.pressure, self.voltage, self.state_of_charge = self.telemetry_unpacker.unpack(
            self.telemetry_socket.recv())

        if self.telemetry_v2_socket.poll(0):
            self.host_ip[0], self.host_ip[1], self.host_ip[2], self.host_ip[3] = self.telemetry_v2_unpacker.unpack(self.telemetry_v2_socket.recv())

        control_message = self.control_packer.pack(
                                    self.is_thrust_in_ms,
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

        self.control_socket.send(control_message)

        rgb_led_colors = [color for led in self.leds_colors for color in led]
        control_v2_message = self.control_v2_packer.pack(*rgb_led_colors)
        self.control_v2_socket.send(control_v2_message)
