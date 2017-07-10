import os
from time import *
import time
import threading
import csv
from collections import namedtuple
from math import cos, sqrt
from geopy.distance import vincenty
import numpy


class Measurement:

    def __init__(self, distance, timestamp, latitude, longitude):
        self.distance = distance
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    @staticmethod
    def read(file_path):
        gps_measurements = []
        distances = []

        with open(file_path, 'r') as captured_file:
            csv_reader = csv.reader(captured_file, delimiter=',')
            distances = []
            i = 0
            last_gps_i = None
            for row in csv_reader:
                sensor_type = row[0]
                timestamp = float(row[1])
                if sensor_type == 'LidarLite':
                    distances.append(LidarLiteMeasurement(timestamp, float(row[2])))
                elif sensor_type == 'GPS':
                    if row[2] != '0.0' and row[3] != '0.0' and (last_gps_i is None or (i - last_gps_i) < 3):
                        gps_measurements.append(GPSMeasurement(timestamp, float(row[2]), float(row[3])))
                    last_gps_i = i
                else:
                    print 'unknown sensor', sensor_type
                i += 1

        distance_index = 0
        while gps_measurements[0].timestamp > distances[distance_index].timestamp:
            distance_index += 1
        gps_index = 0

        print 'read gps measures', len(gps_measurements)
        print 'read distance measures', len(distances)

        measurements = []
        while gps_index < len(gps_measurements) - 1:
            g = gps_measurements[gps_index]
            next_g = gps_measurements[gps_index + 1]

            while distance_index < len(distances) and next_g.timestamp > distances[distance_index].timestamp:
                gps = g.get_interpolation(next_g, distances[distance_index].timestamp)
                measurements.append(Measurement(distances[distance_index].distance, distances[distance_index].timestamp,
                                                gps.latitude, gps.longitude))
                distance_index += 1

            gps_index += 1

        print 'interpolated gps measurements', len(measurements)
        print 'seconds of measurement', measurements[len(measurements) - 1].timestamp - measurements[0].timestamp

        return Measurement.remove_when_the_car_stands(measurements)

    @staticmethod
    def remove_when_the_car_stands(measurements):
        last_m = measurements[0]
        i = 1
        while i < len(measurements):
            m = measurements[i]
            if last_m.latitude == m.latitude and last_m.longitude == m.longitude:
                measurements.pop(i)
            else:
                i += 1
            last_m = m

        print 'filtered standing situations', len(measurements)
        return measurements

class LidarLiteMeasurement:
    def __init__(self, timestamp, distance):
        self.distance = distance
        self.timestamp = timestamp


class GPSMeasurement:
    def __init__(self, timestamp, latitude, longitude):
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    def get_interpolation(self, other_gps, ts):
        lan = self.latitude + (other_gps.latitude - self.latitude)\
                            * (ts - self.timestamp) / (other_gps.timestamp - self.timestamp)
        lon = self.longitude + (other_gps.longitude - self.longitude)\
                             * (ts - self.timestamp) / (other_gps.timestamp - self.timestamp)
        return GPSMeasurement(ts, lan, lon)


if __name__ == '__main__':
    measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_065342_107608.dat')
    # Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat')

