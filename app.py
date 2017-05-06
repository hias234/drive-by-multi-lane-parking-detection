from drive_by_sensing.gps_poller.GpsPoller import GpsPoller
from drive_by_sensing.SensorFileWriter import SensorFileWriter
import time


def p(sensor_name, timestamp, sensed_values):
    print(sensor_name)
    print(sensed_values)

sensor_file_writer = SensorFileWriter('/home/pi/Desktop/data/raw_' + time.time() + '.dat')

gps_poller = GpsPoller(observers=[p, sensor_file_writer.writeLine])
try:
    gps_poller.start()
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
    print "\nKilling Thread..."

gps_poller.running = False
gps_poller.join(timeout=5)
