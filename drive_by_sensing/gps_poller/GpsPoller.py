from ..SensorPoller import SensorPoller
from gps import *


class GpsPoller(SensorPoller):

    def __init__(self, observers=None, sensing_interval_in_s=None):
        SensorPoller.__init__(self, 'GPS', observers=observers, sensing_interval_in_s=sensing_interval_in_s)
        self.gpsd = gps(mode=WATCH_ENABLE)

    def get_sensor_values(self):
        self.gpsd.next()
        return [self.gpsd.fix.latitude, self.gpsd.fix.longitude, self.gpsd.fix.speed]
