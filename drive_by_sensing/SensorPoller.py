from gps import *
import threading
import time
import types


class SensorPoller(threading.Thread):

    def __init__(self, sensor_name, observers=None, sensing_interval_in_s=None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.sensor_name = sensor_name
        self.sensing_interval_in_s = sensing_interval_in_s
        self.observers = observers

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self.setup_sensor()

        while not self.stopped():
            start = time.time()
            sensed_values = self.get_sensor_values()
            end = time.time()

            self.notify_observers(end, sensed_values)

            if self.sensing_interval_in_s is not None:
                time_to_wait = self.sensing_interval_in_s - (end - start)
                if time_to_wait > 0:
                    time.sleep(self.sensing_interval_in_s)
                else:
                    time.sleep(0.0005)

        self.tear_down_sensor()

    def notify_observers(self, timestamp, sensed_values):
        if self.observers is not None:
            if type(self.observers) is list or type(self.observers) is tuple:
                for observer in self.observers:
                    observer(self.sensor_name, timestamp, sensed_values)
            else:
                self.observers(self.sensor_name, timestamp, sensed_values)
        else:
            print(sensed_values)

    def get_sensor_values(self):
        return [-1.0]

    def setup_sensor(self):
        pass

    def tear_down_sensor(self):
        pass
