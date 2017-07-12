import os
from time import *
import time
import threading
import csv
from collections import namedtuple
from math import cos, sqrt
from geopy.distance import vincenty
import numpy
import matplotlib.pyplot as plt

from measurement import Measurement
from visualize import MeasurementVisualization


class MeasureCollection:
    def __init__(self):
        self.measures = []
        self.sum_distance = 0
        self.avg_distance = 0
        self.length = 0
        self.center_latitude = 0
        self.center_longitude = 0
        self.variance = -1.0

    def get_probable_ground_truth(self):
        nr_of_gt_measures = {'NO_PARKING': 0.0, 'PARKING_CAR': 0.0, 'OVERTAKEN_CAR': 0.0}
        for measure in self.measures:
            if measure.ground_truth.is_parking_car:
                nr_of_gt_measures['PARKING_CAR'] += 1
            elif measure.ground_truth.is_overtaken_car:
                nr_of_gt_measures['OVERTAKEN_CAR'] += 1
            else:
                nr_of_gt_measures['NO_PARKING'] += 1

        if self.get_length() > 0.5 and (nr_of_gt_measures['PARKING_CAR'] / len(self.measures)) > 0.7:
            return 'OCCUPIED_PARKING_SPACE'
        if self.get_length() > 0.5 and (nr_of_gt_measures['OVERTAKEN_CAR'] / len(self.measures)) > 0.7:
            return 'OVERTAKEN_CAR'
        return 'NO_PARKING'

    def is_empty(self):
        return len(self.measures) == 0

    def first_measure(self):
        return self.measures[0]

    def last_measure(self):
        return self.measures[len(self.measures) - 1]

    def add_measure_collection(self, measure_collection):
        for measure in measure_collection.measures:
            self.add_measure(measure)

    def add_measure(self, measure):
        self.measures.append(measure)

        self.sum_distance += measure.distance
        self.avg_distance = self.sum_distance / len(self.measures)
        self.length = self.get_length()
        self.variance = -1

        first_measure = self.measures[0]
        last_measure = self.measures[len(self.measures) - 1]

        self.center_longitude = (first_measure.longitude + last_measure.longitude) / 2
        self.center_latitude = (first_measure.latitude + last_measure.latitude) / 2

    def get_length(self):
        length = 0.0
        if len(self.measures) > 0:
            last_measure = self.measures[0]
            for i in range(1, len(self.measures)):
                length += vincenty(
                            (self.measures[i].latitude, self.measures[i].longitude),
                            (last_measure.latitude, last_measure.longitude)
                        ).meters
                last_measure = self.measures[i]

        return length

    def get_distance_variance(self):
        if self.variance != -1.0:
            return self.variance

        sum_top = 0
        for measure in self.measures:
            sum_top = (measure.distance - self.avg_distance)**2

        return sum_top / len(self.measures)


class DriveByEvaluation:

    def __init__(self):
        self.visualize = MeasurementVisualization()

    def filter_flawed_measurements(self, measurements):
        filter_distance_above_threshold = 20
        filter_outlier_distance_threshold = 100
        filter_outlier = True

        i = 0
        filtered_measurements = []
        while i < len(measurements):
            add = True
            if measurements[i].distance <= filter_distance_above_threshold:
                add = False
            elif filter_outlier and 0 < i < len(measurements) - 1:
                diff_to_prev = abs(measurements[i].distance - measurements[i-1].distance)
                diff_to_next = abs(measurements[i].distance - measurements[i+1].distance)
                diff_between_prev_next = abs(measurements[i-1].distance - measurements[i+1].distance)
                if diff_to_next > filter_outlier_distance_threshold \
                        and diff_to_prev > filter_outlier_distance_threshold and diff_between_prev_next < 20:
                    add = False

            if add:
                filtered_measurements.append(measurements[i])
            i += 1

        print 'filtered measurements', len(filtered_measurements)
        return filtered_measurements

    def evaluate(self, measurements):
        measurements = self.filter_flawed_measurements(measurements)

        plateaus = self.get_plateaus(measurements)

        fig = plt.figure(3)
        self.visualize.show_distance_signal_scatter(measurements, fig=fig)

        for plateau in plateaus:
            # print len(plateau.measures), plateau.avg_distance, plateau.get_length(), plateau.get_distance_variance()
            xs = [plateau.first_measure().timestamp, plateau.last_measure().timestamp]
            ys = [plateau.first_measure().distance, plateau.last_measure().distance]
            # ys = [plateau.avg_distance, plateau.avg_distance]
            colors = {'NO_PARKING': 'black', 'OCCUPIED_PARKING_SPACE': 'orange', 'OVERTAKEN_CAR': 'magenta'}
            probable_gt = plateau.get_probable_ground_truth()
            plt.plot(xs, ys, color=colors[probable_gt])
            plt.scatter(xs, ys, color='black', s=5)
        fig.show()

    def get_plateaus(self, measurements):
        abs_to_avg_distance_threshold = 90

        plateaus = []
        cur_plateau = MeasureCollection()
        last_plateau_distance = None
        for measure in measurements:
            if cur_plateau.is_empty() or abs(last_plateau_distance - measure.distance) < abs_to_avg_distance_threshold:
                cur_plateau.add_measure(measure)
            else:
                if len(cur_plateau.measures) > 0:
                    plateaus.append(cur_plateau)
                cur_plateau = MeasureCollection()
                cur_plateau.add_measure(measure)
            last_plateau_distance = measure.distance

        if len(cur_plateau.measures) > 0:
            plateaus.append(cur_plateau)

        print 'found plateaus', len(plateaus)

        #plateaus = self.merge_plateaus(plateaus)

        return plateaus

    def merge_plateaus(self, plateaus):
        threshold_distance_between_ends = 50

        i = 1
        while i < len(plateaus):
            distance_between_ends = abs(plateaus[i-1].last_measure().distance - plateaus[i].first_measure().distance)
            # print distance_between_ends
            if distance_between_ends <= threshold_distance_between_ends:
                plateaus[i-1].add_measure_collection(plateaus[i])
                plateaus.pop(i)
            else:
                i += 1

        print 'merged plateaus', len(plateaus)

        return plateaus

if __name__ == '__main__':
    measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat',
                                    'C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat_images_Camera\\00gt1499703007.98.dat')
    #measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat',
    #                                'C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat_images_Camera\\00gt1499791938.51.dat')
    evaluation = DriveByEvaluation()
    evaluation.evaluate(measurements)
    plt.show()
