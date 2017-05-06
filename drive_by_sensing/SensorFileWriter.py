import csv
import time


class SensorFileWriter:

    def __init__(self, path):
        self.path = path

    def writeLine(self, sensor, sensed_values):
        with open(self.path, 'a') as out:
            csv_out = csv.writer(out)
            csv_out.writerow([sensor, time.time(), sensed_value])
