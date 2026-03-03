import time
from pymurapi.videoserver import VideoServer

class MurApiBase(object):
    """Base class for AUV and Simulator API."""

    def __init__(self):
        self.depth = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.temperature = 0.0
        self.pressure = 0.0
        self.voltage = 0.0
        self.state_of_charge = 0

        self.is_thrust_in_ms = False
        self.colorRGB = [0, 30, 0]
        self.motors_power = [0, 0, 0, 0, 0, 0, 0, 0]
        self.on_delay = 1.5
        self.off_delay = 0.7

        self.leds_colors = list((0,0,0) for i in range(26))
        self.host_ip = [0, 0, 0, 0]

    def _prepare(self):
        pass

    def _update(self):
        pass

    def get_image_front(self):
        """Returns front image. SIMULATOR ONLY!"""
        pass

    def get_image_bottom(self):
        """Returns bottom image. SIMULATOR ONLY!"""
        pass

    def set_on_delay(self, value):
        """Set LED ON delay. If value set to 0 LED will be always OFF"""
        self.on_delay = value

    def set_off_delay(self, value):
        """Set LED OFF delay. If value set to 0 LED will be always ON"""
        self.off_delay = value

    def set_rgb_color(self, r, g, b):
        """Set LED color in RGB colorspace. Values are 0 - 255"""
        self.colorRGB = [int(r), int(g), int(b)]
        self.leds_colors = list((int(r),int(g),int(b)) for i in range(26))


    def set_single_led_color(self, index, r, g, b):
        """Set single LED color in RGB colorspace. First value is LED number.
           Next 3 values are RGB color (0 - 255)"""
        self.leds_colors[index] = [int(r), int(g), int(b)]

    def set_motor_power(self, motor_id, power):
        """Set motor (motor_id 0 - 8) power. Values can be between 2 ** 15 and -2 ** 15 if thrust in ms enabled.
           Values can be between 100 and -100 if thrust in ms disabled.
        """
        if motor_id < 0 or motor_id > 8:
            return
        if abs(power) > 32767:
            return
        self.motors_power[int(motor_id)] = int(power)

    def set_enable_power_in_ms(self, enabled):
        """Set power in ms mode enabled(True)  or disabled(False)"""
        self.is_thrust_in_ms = enabled

    def get_depth(self):
        """Returns current depth in meters."""
        return self.depth

    def get_yaw(self):
        """Returns current yaw in degrees from -180 to 180"""
        return self.yaw

    def get_pitch(self):
        """Returns current pitch in degrees from -180 to 180."""
        return self.pitch

    def get_roll(self):
        """Returns current roll in degrees from -180 to 180."""
        return self.roll

    def get_temperature(self):
        """Returns current temperature in Celsius."""
        return self.temperature

    def get_pressure(self):
        """Returns current outer pressure in Pascals."""
        return self.pressure

    def get_voltage(self):
        """Returns current voltage in volts. i.e. 12.3"""
        return self.voltage
    
    def get_state_of_charge(self):
        """Returns state of charge in percent"""
        return self.state_of_charge

    def get_host_ip(self):
        """Return current host computer IP address"""
        return "{}.{}.{}.{}".format(self.host_ip[0], self.host_ip[1], self.host_ip[2], self.host_ip[3])

    def get_videoserver(self, host=None):
        """Return VideoServer for streaming to MUR IDE camera views"""
        
        if host is None:
            host = self.get_host_ip()
        
        if host == "0.0.0.0":
            host = "10.3.141.0"

        return VideoServer(host=host)
