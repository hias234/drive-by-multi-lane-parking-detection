from gps_poller.GpsPoller import GpsPoller
from time import sleep


def p(sensed_value):
    print(sensed_value)

gps_poller = GpsPoller(p, None)
try:
    gps_poller.run()
    while True:
        sleep(1)

except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
    print "\nKilling Thread..."

gps_poller.running = False
gps_poller.join(timeout=5)
