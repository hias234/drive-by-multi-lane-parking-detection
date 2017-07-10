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
from mpl_toolkits.mplot3d import Axes3D

from measurement import Measurement

class MeasurementVisualization:

    def show_distance_signal(self, measurements):
        fig = plt.figure(1)
        xs = [raw.timestamp for raw in measurements]
        ys = [raw.distance for raw in measurements]

        plt.plot(xs, ys)

        fig.show()

    def show_3d(self, measurements):
        fig = plt.figure(2)
        ax = fig.add_subplot(111, projection='3d')

        xs = [raw.latitude for raw in measurements]
        ys = [raw.longitude for raw in measurements]
        zs = [raw.distance for raw in measurements]

        ax.scatter(xs, ys, zs, 'z', depthshade=True)

        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        ax.set_zlabel('Distance')

        fig.show()

if __name__ == '__main__':
    measurements = Measurement.read('C:\\sw\\master\\collected data\\data\\raw_20170705_065342_107608.dat')

    visualization = MeasurementVisualization()
    visualization.show_distance_signal(measurements)
    visualization.show_3d(measurements)
    plt.show()
