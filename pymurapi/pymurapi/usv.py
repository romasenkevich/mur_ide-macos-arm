import threading
import zmq
import struct
import time
from pymurapi import api


class Usv(api.MurApiBase, threading.Thread):
    battery = 100.0
    lat_to = 0.0
    lng_to = 0.0
    gps_satellites = 0
    gps_alt = 0.0
    gps_lat = 0.0
    gps_lng = 0.0
    gps_speed = 0.0
    gps_yaw = 0.0

    def __init__(self):
        threading.Thread.__init__(self, daemon=False)
        api.MurApiBase.__init__(self)

        ctx = zmq.Context()
        # telemetry bin
        self.unpacker = struct.Struct('=b9f')
        # control bin b8h3B2f
        self.packer = struct.Struct('=4h4B4f')
        self.telemetry_socket = ctx.socket(zmq.SUB)
        self.control_socket = ctx.socket(zmq.PAIR)

    def run(self):
        while True:
            self._update()
            time.sleep(0.001)

    def prepare(self):
        telemetry_url = "tcp://127.0.0.1:2001"
        control_url = "tcp://127.0.0.1:2002"

        self.telemetry_socket.connect(telemetry_url)
        self.telemetry_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.telemetry_socket.setsockopt(zmq.LINGER, 0)

        self.control_socket.connect(control_url)
        self.control_socket.setsockopt(zmq.SNDTIMEO, 3000)

        self.start()

    def _update(self):
        self.gps_satellites,\
            self.gps_alt,\
            self.gps_lat,\
            self.gps_lng,\
            self.gps_speed,\
            self.gps_yaw,\
            self.roll,\
            self.pitch,\
            self.yaw,\
            self.battery = self.unpacker.unpack(self.telemetry_socket.recv())

        message = self.packer.pack(self.motors_power[0],
                                   self.motors_power[1],
                                   self.motors_power[2],
                                   self.motors_power[3],
                                   self.is_thrust_in_ms,
                                   self.colorRGB[0],
                                   self.colorRGB[1],
                                   self.colorRGB[2],
                                   self.on_delay,
                                   self.off_delay,
                                   self.lat_to,
                                   self.lng_to)

        self.control_socket.send(message)

    def set_servo(self, angle):
        super().set_motor_power(2, angle)

    def set_motor_power(self, motor_id, power):
        if motor_id != 2:
            super().set_motor_power(motor_id, power)

    def set_point_to(self, lat, lng):
        self.lat_to = float(lat)
        self.lng_to = float(lng)

    def get_gps_satellites(self):
        return self.gps_satellites

    def get_gps_alt(self):
        return self.gps_alt

    def get_gps_lat(self):
        return self.gps_lat

    def get_gps_lng(self):
        return self.gps_lng

    def get_gps_speed(self):
        return self.gps_speed

    def get_gps_yaw(self):
        return self.gps_yaw

