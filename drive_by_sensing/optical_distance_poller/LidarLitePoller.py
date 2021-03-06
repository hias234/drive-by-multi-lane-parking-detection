from ..SensorPoller import SensorPoller
import smbus
import time


class LidarLitePoller(SensorPoller):

    def __init__(self, observers=None, sensing_interval_in_s=None):
        SensorPoller.__init__(self, 'LidarLite', observers=observers, sensing_interval_in_s=sensing_interval_in_s)
        self.lidar = LidarLite()

    def setup_sensor(self):
        connected = self.lidar.connect(1)

        if connected < 0:
            print "NOT CONNECTED -> EXITING"
            self.running = False

    def get_sensor_values(self):
        return [self.lidar.getDistance()]


class LidarLite:
    def __init__(self):
        self.address = 0x62
        self.distWriteReg = 0x00
        self.distWriteVal = 0x04
        self.distReadReg1 = 0x8f
        self.distReadReg2 = 0x10
        self.velWriteReg = 0x04
        self.velWriteVal = 0x08
        self.velReadReg = 0x09

        # value from github 0.02
        self.waitAfterRead = 0.001
        # self.waitAfterRead = 0.02

    def connect(self, bus):
        try:
            self.bus = smbus.SMBus(bus)
            time.sleep(0.5)
            return 0
        except:
            return -1

    def writeAndWait(self, register, value):
        self.bus.write_byte_data(self.address, register, value)
        time.sleep(self.waitAfterRead)

    def readAndWait(self, register):
        res = self.bus.read_byte_data(self.address, register)
        time.sleep(self.waitAfterRead)
        return res

    def getDistance(self):
        self.writeAndWait(self.distWriteReg, self.distWriteVal)
        dist1 = self.readAndWait(self.distReadReg1)
        dist2 = self.readAndWait(self.distReadReg2)
        return (dist1 << 8) + dist2

    def getVelocity(self):
        self.writeAndWait(self.distWriteReg, self.distWriteVal)
        self.writeAndWait(self.velWriteReg, self.velWriteVal)
        vel = self.readAndWait(self.velReadReg)
        return self.signedInt(vel)

    def signedInt(self, value):
        if value > 127:
            return (256-value) * (-1)
        else:
            return value

