from ..SensorPoller import SensorPoller
import pygame, sys
from pygame.locals import *
import pygame.camera


class CameraPoller(SensorPoller):

    def __init__(self, observers=None, sensing_interval_in_s=None):
        SensorPoller.__init__(self, 'Camera', observers=observers, sensing_interval_in_s=sensing_interval_in_s)

        print "init camera poller"

        pygame.init()
        pygame.camera.init()
        self.cam = pygame.camera.Camera("/dev/video0", (352, 288))

        print "init camera poller succeeded"

    def get_sensor_values(self):
        print "get_image"
        image = self.cam.get_image()
        print "got image "
        return [image]

    def setup_sensor(self):
        self.cam.start()

    def tear_down_sensor(self):
        self.cam.stop()
