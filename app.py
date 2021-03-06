from drive_by_sensing.optical_distance_poller.LidarLitePoller import LidarLitePoller
from drive_by_sensing.gps_poller.GpsPoller import GpsPoller
from drive_by_sensing.camera_poller.CameraPoller import CameraPoller
from drive_by_sensing.SensorFileWriter import SensorFileWriter
import time
import datetime


def p(sensor_name, timestamp, sensed_values):
    print(timestamp, sensor_name, sensed_values)

sensor_file_writer = SensorFileWriter('/home/pi/Desktop/master/data/raw_' + datetime.datetime.now()
                                      .strftime('%Y%m%d_%H%M%S_%f') + '.dat')

lidar_poller = LidarLitePoller(observers=[p, sensor_file_writer.write_csv_line], sensing_interval_in_s=0.001)
gps_poller = GpsPoller(observers=[p, sensor_file_writer.write_csv_line])
camera_poller = CameraPoller(observers=[sensor_file_writer.write_image_async], sensing_interval_in_s=0.005)
# gps_poller = GpsPoller(observers=[p])
try:
    gps_poller.start()
    lidar_poller.start()
    camera_poller.start()
    while True:
        time.sleep(0.5)

except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
    print "\nKilling Thread..."

gps_poller.stop()
lidar_poller.stop()
camera_poller.stop()
gps_poller.join(timeout=5)
lidar_poller.join(timeout=5)
camera_poller.join(timeout=5)

if gps_poller.isAlive():
    print "gps-poller is alive :("
if lidar_poller.isAlive():
    print "lidar-poller is alive :("
if camera_poller.isAlive():
    print "camera-poller is alive :("
