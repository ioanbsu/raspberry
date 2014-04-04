# !/usr/bin/python

# 3axis gyroscope

# import smbus to access i2c port
import math

SENSOR_READ_ADDRESS = 0x69


class L3G4200D:
    def __init__(self, bus):
        self.i2c_bus = bus
        # initialise the L3G4200D
        # normal mode and all axes on to control reg1
        self.i2c_bus.write_byte_data(SENSOR_READ_ADDRESS, 0x20, 0x0F)
        # full 2000dps to control reg4
        self.i2c_bus.write_byte_data(SENSOR_READ_ADDRESS, 0x23, 0x30)
        # setting low-pass and high-pass filter
        self.i2c_bus.write_byte_data(SENSOR_READ_ADDRESS, 0x24, 0x58)
        # setting stream mode
        self.i2c_bus.write_byte_data(SENSOR_READ_ADDRESS, 0x2e, 0x40)

    def getSignedNumber(self, number):
        if number & (1 << 15):
            return number | ~65535
        else:
            return number & 65535


    # read lower and upper bytes, combine and display
    def getAxeData(self, lAddr, hAddr):
        self.i2c_bus.write_byte(SENSOR_READ_ADDRESS, lAddr)
        lValue = self.i2c_bus.read_byte(SENSOR_READ_ADDRESS)
        self.i2c_bus.write_byte(SENSOR_READ_ADDRESS, hAddr)
        hValue = self.i2c_bus.read_byte(SENSOR_READ_ADDRESS)
        signedValue = hValue << 8 | lValue
        return self.getSignedNumber(signedValue)

    def getSpeeds(self):
        xSpeed =self.getAxeData(0x28, 0x29)
        ySpeed= self.getAxeData(0x2A, 0x2B)
        zSpeed=self.getAxeData(0x2C, 0x2D)

        radiansAroundZ = math.radians(45 + 180)

        newX = (math.cos(radiansAroundZ) * xSpeed - math.sin(radiansAroundZ) * ySpeed)
        newY = math.sin(radiansAroundZ) * xSpeed + math.cos(radiansAroundZ) * ySpeed

        return {"x": newX, "y": newY * -1, "z": zSpeed*-1}

    def getTemperature(self):
        self.i2c_bus.write_byte(SENSOR_READ_ADDRESS, 0x26)
        temp = self.getSignedNumber(self.i2c_bus.read_byte(SENSOR_READ_ADDRESS))
        return temp