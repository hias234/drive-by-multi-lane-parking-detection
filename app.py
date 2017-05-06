from drive_by_sensing.optical_distance_poller.LidarLitePoller import LidarLitePoller
from drive_by_sensing.gps_poller.GpsPoller import GpsPoller
from drive_by_sensing.SensorFileWriter import SensorFileWriter
import time


def p(sensor_name, timestamp, sensed_values):
    print(sensor_name)
    print(sensed_values)

sensor_file_writer = SensorFileWriter('/home/pi/Desktop/data/raw_' + str(time.time()) + '.dat')

lidar_poller = LidarLitePoller(observers=p, sensing_interval_in_s=1)
gps_poller = GpsPoller(observers=[p, sensor_file_writer.writeLine])
try:
    gps_poller.start()
    lidar_poller.start()
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
    print "\nKilling Thread..."

gps_poller.running = False
gps_poller.join(timeout=5)

lidar_poller.running = False
lidar_poller.join(timeout=5)
