import csv
import time


class SensorFileWriter:

    def __init__(self, path):
        self.path = path

    def writeLine(self, sensor_name, timestamp, sensed_values):
        csv_row = [sensor_name, timestamp]
        csv_row.extend(sensed_values)

        with open(self.path, 'a') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(csv_row)
