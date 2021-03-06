import os
from time import *
import time
import threading
import csv
from collections import namedtuple
from math import cos, sqrt
from geopy.distance import vincenty
import numpy as np
import matplotlib.pyplot as plt

from measurement import Measurement
from visualize import MeasurementVisualization
from measure_collection import MeasureCollection

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

        plateaus = MeasureCollection.create_measure_collections(measurements)

        fig = plt.figure(3)
        self.visualize.show_distance_signal_scatter(measurements, fig=fig)
        #self.visualize.show_distance_signal_low_pass(measurements, fig=fig)

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

        first_plateaus = plateaus[50:70]
        plateau_avg_distances = [p.avg_distance for p in first_plateaus]
        bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 100000]
        freq, bins = np.histogram(plateau_avg_distances, bins, weights=[len(p.measures) for p in first_plateaus])
        for i in range(0, len(bins)-1):
            print bins[i], freq[i]

if __name__ == '__main__':
    #measurements = Measurement.read('C:\\sw\\master\\collected data\\data_20170707\\raw_20170705_065613_869794.dat',
    #                                'C:\\sw\\master\\collected data\\data_20170707\\raw_20170705_065613_869794.dat_images_Camera\\00gt1499703007.98.dat')
    #measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat',
    #                                'C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat_images_Camera\\00gt1499791938.51.dat')
    # measurements = Measurement.read('C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074348_696382.dat',
    #                                'C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074348_696382.dat_images_Camera\\00gt1500398878.87.dat')
    measurements = Measurement.read('C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074500_002138.dat',
                                    'C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074500_002138.dat_images_Camera\\00gt1500400602.86.dat')
    #plateaus = MeasureCollection.create_measure_collections(measurements)
    #MeasureCollection.write_to_file('C:\\sw\\master\\collected data\\data_20170707\\tagged_mc_20170705_065613_869794.dat', plateaus)
    evaluation = DriveByEvaluation()
    evaluation.evaluate(measurements)

    #bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 100000]
    #bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 100000]
    #print bins
    #freq, bins = np.histogram([measure.distance for measure in measurements], bins)
    #for i in range(0,len(bins)):
    #    print bins[i], freq[i]

    plt.show()
