from ..SensorPoller import SensorPoller
from gps import *


class GpsPoller(SensorPoller):

    def __init__(self, observers=None, sensing_interval_in_s=None):
        SensorPoller.__init__(self, 'GPS', observers=observers, sensing_interval_in_s=sensing_interval_in_s)
        self.gpsd = gps(mode=WATCH_ENABLE)

    def get_sensor_values(self):
        current_gps = self.gpsd.next()
        return [current_gps.fix.latitude, current_gps.fix.longitude]
