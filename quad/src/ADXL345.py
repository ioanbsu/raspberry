# axelerometer

import math
# ADXL345 constants
EARTH_GRAVITY_MS2 = 9.80665
SCALE_MULTIPLIER = 0.0042

DATA_READ_ADDRESS = 0x53


DATA_FORMAT = 0x31
BW_RATE = 0x2C
POWER_CTL = 0x2D

BW_RATE_1600HZ = 0x0F
BW_RATE_800HZ = 0x0E
BW_RATE_400HZ = 0x0D
BW_RATE_200HZ = 0x0C
BW_RATE_100HZ = 0x0B
BW_RATE_50HZ = 0x0A
BW_RATE_25HZ = 0x09

RANGE_2G = 0x00
RANGE_4G = 0x01
RANGE_8G = 0x02
RANGE_16G = 0x03

MEASURE = 0x08
AXES_DATA = 0x32


class ADXL345:
    address = None
    bus = None

    def __init__(self, bus):
        self.bus = bus
        self.address = DATA_READ_ADDRESS
        self.setBandwidthRate(BW_RATE_100HZ)
        self.setRange(RANGE_2G)
        self.enableMeasurement()

    def enableMeasurement(self):
        self.bus.write_byte_data(self.address, POWER_CTL, MEASURE)

    def setBandwidthRate(self, rate_flag):
        self.bus.write_byte_data(self.address, BW_RATE, rate_flag)

    # set the measurement range for 10-bit readings
    def setRange(self, range_flag):
        value = self.bus.read_byte_data(self.address, DATA_FORMAT)

        value &= ~0x0F
        value |= range_flag
        value |= 0x08

        self.bus.write_byte_data(self.address, DATA_FORMAT, value)

    # returns the current reading from the sensor for each axis
    #
    # parameter gforce:
    # False (default): result is returned in m/s^2
    # True           : result is returned in gs
    def getAxes(self, gforce=False):
        bytes = self.bus.read_i2c_block_data(self.address, AXES_DATA, 6)

        x = bytes[0] | (bytes[1] << 8)
        if (x & (1 << 16 - 1)):
            x = x - (1 << 16)

        y = bytes[2] | (bytes[3] << 8)
        if (y & (1 << 16 - 1)):
            y = y - (1 << 16)

        z = bytes[4] | (bytes[5] << 8)
        if (z & (1 << 16 - 1)):
            z = z - (1 << 16)

        x = x * SCALE_MULTIPLIER
        y = y * SCALE_MULTIPLIER
        z = z * SCALE_MULTIPLIER

        if gforce == False:
            x = x * EARTH_GRAVITY_MS2
            y = y * EARTH_GRAVITY_MS2
            z = z * EARTH_GRAVITY_MS2

        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)

        radiansAroundZ = math.radians(45 + 180)
        newX = (math.cos(radiansAroundZ) * x - math.sin(radiansAroundZ) * y)
        newY = math.sin(radiansAroundZ) * x + math.cos(radiansAroundZ) * y

        return {"x": newX, "y": newY * -1, "z": z}


    def _get_rotation(self, x, y, z):
        return math.atan(x / math.sqrt((y * y) + (z * z)))

    def getRotations(self, hmc58883l):
        axes = self.getAxes(True)
        yRotation = self._get_rotation(axes['x'], axes['z'], axes['y'])
        xRotation = self._get_rotation(axes['y'], axes['z'], axes['x'])
        return {"x": xRotation, "y": yRotation, "z": hmc58883l.heading()}


if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output
    # the current readings
    adxl345 = ADXL345()

    axes = adxl345.getAxes(True)
    print "ADXL345 on address 0x%x:" % (adxl345.address)
    print "   x = %.3fG" % ( axes['x'] )
    print "   y = %.3fG" % ( axes['y'] )
    print "   z = %.3fG" % ( axes['z'] )