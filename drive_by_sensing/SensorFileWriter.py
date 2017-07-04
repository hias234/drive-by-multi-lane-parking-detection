import os
import csv
import time
import pygame, sys
from pygame.locals import *
import pygame.camera
import time
import datetime
import threading


class SensorFileWriter:

    def __init__(self, path):
        self.path = path

    def write_image_async(self, sensor_name, timestamp, sensed_values):
        t = threading.Thread(target=self.write_image, args=(sensor_name, timestamp, sensed_values))
        t.start()

    def write_image(self, sensor_name, timestamp, sensed_values):
        image_path = self.path + '_images_' + sensor_name
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        print "save image to " + image_path

        pygame.image.save(sensed_values[0], image_path + '/' +
                          # datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S_%f')
                          str(timestamp) + '.jpg')

    def write_csv_line(self, sensor_name, timestamp, sensed_values):
        csv_row = [sensor_name, timestamp]
        csv_row.extend(sensed_values)

        with open(self.path, 'a') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(csv_row)
