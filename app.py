from drive_by_sensing.gps_poller.GpsPoller import GpsPoller
from time import sleep


def p(sensor_name, sensed_values):
    print(sensor_name + " " + sensed_values)

gps_poller = GpsPoller(observers=p)
try:
    gps_poller.start()
    while True:
        sleep(1)

except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
    print "\nKilling Thread..."

gps_poller.running = False
gps_poller.join(timeout=5)
