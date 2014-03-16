# i2C BMP085 Pressure & Temperature Sensor Driver

import smbus
import time

DATA_READ_ADDRESS = 0x77


class BMP085():
    OSS = 3

    def __init__(self, i2c):
        self.i2c = i2c
        self.address = DATA_READ_ADDRESS
        self.ac1 = self.readSignedWord(0xaa)
        self.ac2 = self.readSignedWord(0xac)
        self.ac3 = self.readSignedWord(0xae)
        self.ac4 = self.readWord(0xb0)
        self.ac5 = self.readWord(0xb2)
        self.ac6 = self.readWord(0xb4)
        self.b1 = self.readSignedWord(0xb6)
        self.b2 = self.readSignedWord(0xb8)
        self.mb = self.readSignedWord(0xba)
        self.mc = self.readSignedWord(0xbc)
        self.md = self.readSignedWord(0xbe)

    def readWord(self, reg):
        msb = self.i2c.read_byte_data(self.address, reg)
        lsb = self.i2c.read_byte_data(self.address, reg + 1)
        value = (msb << 8) + lsb
        return value

    def readSignedWord(self, reg):
        msb = self.i2c.read_byte_data(self.address, reg)
        lsb = self.i2c.read_byte_data(self.address, reg + 1)
        if (msb > 127):
            msb = msb - 256
        value = (msb << 8) + lsb
        return value

    def readUT(self):
        self.i2c.write_byte_data(self.address, 0xf4, 0x2e)
        time.sleep(0.0045)
        ut = self.readWord(0xf6)
        return ut

    def readTemperature(self):
        ut = self.readUT()
        x1 = ((ut - self.ac6) * self.ac5) >> 15
        x2 = (self.mc << 11) / (x1 + self.md)
        self.b5 = x1 + x2
        return ((self.b5 + 8) >> 4) / 10.0

    def readUP(self):
        self.i2c.write_byte_data(self.address, 0xf4, 0x34 + (self.OSS << 6))
        delay = (2 + (3 << self.OSS)) / 1000.0
        time.sleep(delay)
        msb = self.i2c.read_byte_data(self.address, 0xf6)
        lsb = self.i2c.read_byte_data(self.address, 0xf7)
        xlsb = self.i2c.read_byte_data(self.address, 0xf8)
        up = (msb << 16) + (lsb << 8) + xlsb
        up = up >> (8 - self.OSS)
        return up

    def readPressure(self):
        up = self.readUP()

        b6 = self.b5 - 4000

        x1 = (self.b2 * (b6 * b6) >> 12) >> 11
        x2 = (self.ac2 * b6) >> 11
        x3 = x1 + x2
        b3 = (((self.ac1 * 4 + x3) << self.OSS) + 2) >> 2

        x1 = (self.ac3 * b6) >> 13
        x2 = (self.b1 * ((b6 * b6) >> 12)) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        b4 = (self.ac4 * (x3 + 32768)) >> 15

        b7 = (up - b3) * (50000 >> self.OSS)

        if (b7 < 0x80000000):
            p = (b7 << 1) / b4
        else:
            p = (b7 / b4) << 1

        x1 = (p >> 8) * (p >> 8)
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * p) >> 16
        p += (x1 + x2 + 3791) >> 4

        return p/100.


