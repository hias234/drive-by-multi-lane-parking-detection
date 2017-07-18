import os
from time import *
import time
import threading
import csv
from collections import namedtuple
from math import cos, sqrt
from geopy.distance import vincenty
import numpy as np
import scipy
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import gmplot
from mpl_toolkits.mplot3d import Axes3D

from measurement import Measurement
from measure_collection import MeasureCollection


class MeasurementVisualization:

    def show_distance_signal(self, measurements, fig=None):
        if fig is None:
            fig = plt.figure(4)
        # xs = []
        # length = 0
        # for index in range(1, len(measurements)):
        #     xs.append(length)
        #     length += vincenty(
        #                     (measurements[index - 1].latitude, measurements[index - 1].longitude),
        #                     (measurements[index].latitude, measurements[index].longitude)
        #                 ).meters
        # xs.append(length)
        xs = [raw.timestamp for raw in measurements]
        ys = [raw.distance for raw in measurements]

        plt.plot(xs, ys)

        #median_distance = np.mean(ys)
        #plt.plot([xs[0], xs[len(xs) - 1]], [median_distance, median_distance])

        fig.show()

    def show_distance_signal_low_pass(self, measurements,  fig=None):
        if fig is None:
            fig = plt.figure(5)

        xs = [raw.timestamp for raw in measurements]
        ys = [raw.distance for raw in measurements]

        fs = 10E9  # 1 ns -> 1 GHz
        cutoff = 10E6  # 10 MHz
        B, A = butter(1, cutoff / (fs / 2), btype='low')  # 1st order Butterworth low-pass
        ys_filtered = lfilter(B, A, ys, axis=0)

        #bz, az = scipy.signal.butter(0, 1 / (200 / 2))  # Gives you lowpass Butterworth as default
        #ys_filtered = scipy.signal.filtfilt(bz, az, input)  # Makes forward/reverse filtering (linear phase filter)

        plt.plot(xs, ys)
        plt.plot(xs, ys_filtered)

        fig.show()

    def show_distance_signal_scatter(self, measurements, fig=None):
        if fig is None:
            fig = plt.figure(1)
        xs = [raw.timestamp for raw in measurements]
        ys = [raw.distance for raw in measurements]
        cs = self.get_color_list(measurements)

        plt.scatter(xs, ys, c=cs)

        fig.show()

    def get_color_list(self, measurements):
        cs = []
        for raw in measurements:
            if raw.ground_truth.is_parking_car:
                cs.append('g')
            elif raw.ground_truth.is_overtaken_car:
                cs.append('r')
            else:
                cs.append('y')
        return cs

    def show_3d(self, measurements, fig=None):
        if fig is None:
            fig = plt.figure(2)
        ax = fig.add_subplot(111, projection='3d')

        xs = [raw.latitude for raw in measurements]
        ys = [raw.longitude for raw in measurements]
        zs = [raw.distance for raw in measurements]
        cs = self.get_color_list(measurements)

        ax.scatter(xs, ys, zs, 'z', c=cs, depthshade=True)

        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        ax.set_zlabel('Distance')

        fig.show()

    def show_gps_locations(self, measurements):
        gmap = gmplot.GoogleMapPlotter(48.3045, 14.291153333, 16)
        gmap.scatter([raw.latitude for raw in measurements], [raw.longitude for raw in measurements],
                     '#3B0B39', size=1, marker=False)

        gmap.draw("C:\\sw\\master\\mymap1.html")


    def show_distances_plus_segmentation(self, measure_collections, fig=None):
        if fig is None:
            fig = plt.figure(8)
        for measure_collection in measure_collections:
            self.show_distance_signal_scatter(measure_collection.measures, fig=fig)
            # print len(plateau.measures), plateau.avg_distance, plateau.get_length(), plateau.get_distance_variance()
            xs = [measure_collection.first_measure().timestamp, measure_collection.last_measure().timestamp]
            ys = [measure_collection.first_measure().distance, measure_collection.last_measure().distance]
            # ys = [plateau.avg_distance, plateau.avg_distance]
            colors = {'NO_PARKING': 'black', 'OCCUPIED_PARKING_SPACE': 'orange', 'OVERTAKEN_CAR': 'magenta'}
            probable_gt = measure_collection.get_probable_ground_truth()
            plt.plot(xs, ys, color=colors[probable_gt])
            plt.scatter(xs, ys, color='black', s=5)
        fig.show()

if __name__ == '__main__':
    #measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat',
    #                                'C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat_images_Camera\\00gt1499703007.98.dat')
    #measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat',
    #                                'C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat_images_Camera\\00gt1499791938.51.dat')
    visualization = MeasurementVisualization()
    measure_collections = MeasureCollection.read_from_file('C:\\sw\\master\\collected data\\data_20170707\\tagged_mc_20170705_065613_869794.dat')
    visualization.show_distances_plus_segmentation(measure_collections)
    #visualization.show_distance_signal(measurements)
    #visualization.show_3d(measurements)
    #visualization.show_gps_locations(measurements)
    plt.show()
