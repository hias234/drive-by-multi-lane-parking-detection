from drive_by_sensing.SensorPoller import SensorPoller
from gps import *


class GpsPoller(SensorPoller):

    def __init__(self, observers, sensing_interval_in_s):
        SensorPoller.__init__(self, observers, sensing_interval_in_s)
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.gpsd.start()

    def get_sensor_value(self):
        return self.gpsd.next()
