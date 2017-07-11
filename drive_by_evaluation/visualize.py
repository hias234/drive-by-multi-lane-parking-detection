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
import gmplot
from mpl_toolkits.mplot3d import Axes3D

from measurement import Measurement

class MeasurementVisualization:

    def show_distance_signal(self, measurements):
        fig = plt.figure(1)
        xs = [raw.timestamp for raw in measurements]
        ys = [raw.distance for raw in measurements]

        plt.plot(xs, ys)

        fig.show()

    def show_distance_signal_scatter(self, measurements):
        fig = plt.figure(1)
        xs = [raw.timestamp for raw in measurements]
        ys = [raw.distance for raw in measurements]
        cs = []
        for raw in measurements:
            if raw.ground_truth.is_parking_car:
                cs.append('r')
            else:
                cs.append('b')

        plt.scatter(xs, ys, c=cs)

        fig.show()

    def show_3d(self, measurements):
        fig = plt.figure(2)
        ax = fig.add_subplot(111, projection='3d')

        xs = [raw.latitude for raw in measurements]
        ys = [raw.longitude for raw in measurements]
        zs = [raw.distance for raw in measurements]
        cs = []
        for raw in measurements:
            if raw.ground_truth.is_parking_car:
                cs.append('r')
            else:
                cs.append('b')

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



if __name__ == '__main__':
    measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat',
                                    'C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat_images_Camera\\00gt1499703007.98.dat')
    #measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_064859_283466.dat', None)
    visualization = MeasurementVisualization()
    visualization.show_distance_signal_scatter(measurements)
    visualization.show_3d(measurements)
    #visualization.show_gps_locations(measurements)
    plt.show()
