from gps import *
import threading
import time
import types


class SensorPoller(threading.Thread):

    def __init__(self, sensor_name, observers=None, sensing_interval_in_s=None):
        threading.Thread.__init__(self)
        self.running = True
        self.sensor_name = sensor_name
        self.sensing_interval_in_s = sensing_interval_in_s
        self.observers = observers

    def run(self):
        while self.running:
            sensed_values = self.get_sensor_values()

            self.notify_observers(sensed_values)

            if self.sensing_interval_in_s is not None:
                time.sleep(self.sensing_interval_in_s)

    def notify_observers(self, sensed_values):
        if self.observers is not None:
            if type(self.observers) is list or type(self.observers) is tuple:
                for observer in self.observers:
                    observer(self.sensor_name, sensed_values)
            else:
                self.observers(self.sensor_name, sensed_values)
        else:
            print(sensed_values)

    def get_sensor_values(self):
        return [-1.0]
