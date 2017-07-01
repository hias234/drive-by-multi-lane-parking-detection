import os
from time import *
import time
import threading
import csv
from collections import namedtuple
from math import cos, sqrt
# from geopy.distance import vincenty
import numpy

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

RawMeasure = namedtuple('raw_measure', 'distance latitude longitude timestamp gt_ps_beside gt_ps_occupied')

# comment in which measurements you want to evaluate
#dir = "./m20170701_0_5ms_interval/"
dir = "./m20170701_20ms_interval/"
#defined_distances = [6,30,75,125,150,175,200,250,300,400]

defined_distances = [10,20,50,100,150,200,400,600,1000,1500]

means = []
stds = []
err_ranges = []

for root, dirs, files in os.walk(dir):
    files.sort()
    i = 0
    for file in files:
        with open(dir + file, 'r') as captured_file:
            csv_reader = csv.reader(captured_file, delimiter=',')
            distances = []
            errors = []
            for row in csv_reader:
                sensor = row[0]
                if sensor == 'LidarLite':
                    timestamp = float(row[1])
                    distance = float(row[2])
                    #latitude = float(row[2])
                    #longitude = float(row[3])
                    #gt_ps_beside = row[4] == 'True'
                    #gt_ps_occupied = row[5] == 'True'

                    # if the distance is smaller or equals zero, then there was a timeout
                    if distance <= 1:
                        distance = 10000
                    #if distance > 10000:
                    #    distance = 1000

                    distances.append(distance)
                    errors.append(defined_distances[i] - distance)

            #show_scatter_plot(raw_measures)
            means.append(numpy.mean(distances))
            stds.append(numpy.std(distances))

            err_range = float(len([1 for d in distances if defined_distances[i] * 0.8 < d < defined_distances[i] * 1.2])) / len(distances)
            err_ranges.append(err_range)

            print defined_distances[i]
            print numpy.mean(distances), numpy.std(distances)
            print numpy.max(distances), numpy.min(distances)
            print err_range
            print ''
            i += 1

fig = plt.figure(1)

defined_distances_display = [10,20,50,100,150,200,400,600,1000,1500]

plt.plot(defined_distances_display, defined_distances, c='r')
plt.scatter(defined_distances_display, defined_distances, c='r')


plt.plot(defined_distances_display, means)
plt.scatter(defined_distances_display, means, marker='^')
plt.errorbar(defined_distances_display, means, stds, linestyle='None', marker='^')

plt.xlabel('Distance')
plt.ylabel('Measured Distance')

fig.show()

fig2 = plt.figure(2)
plt.plot(defined_distances, err_ranges, c='y')
plt.scatter(defined_distances, err_ranges, c='y')
fig2.show()

plt.show()
