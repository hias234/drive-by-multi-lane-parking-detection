from gps import *
import threading
import time
import types


class SensorPoller(threading.Thread):

    def __init__(self, oberservers=None, sensing_interval_in_s=None):
        threading.Thread.__init__(self)
        self.running = True
        self.sensing_interval_in_s = sensing_interval_in_s
        self.observers = oberservers

    def run(self):
        while self.running:
            sensed_value = self.get_sensor_value()

            self.notify_observers(sensed_value)

            if self.sensing_interval_in_s is not None:
                time.sleep(self.sensing_interval_in_s)

    def notify_observers(self, sensed_value):
        if self.observers is not None:
            if type(self.observers) is list or type(self.observers) is tuple:
                for observer in self.observers:
                    observer(sensed_value)
            else:
                self.observers(sensed_value)
        else:
            print(sensed_value)

    def get_sensor_value(self):
        return -1.0
