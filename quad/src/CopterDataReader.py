import sys

import smbus
from ADXL345 import ADXL345
from myQuad.HMC58883l import HMC5883l
from L3G4200D import L3G4200D
from src import BMP085


class CopterDataReader:
    revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
    bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

    adxl345 = ADXL345(bus)
    bmp085 = BMP085(bus)
    hmc58883l = HMC5883l(bus)
    l3g4200d = L3G4200D(bus)


    def __init__(self, adxl_smoothing=100, l3g4200d_smooting=10, hmc58883l_smoothing=10, bmp085_smoothing=10):
        self.adxl_smoothing = adxl_smoothing
        self.l3g4200d_smooting = l3g4200d_smooting
        self.hmc58883l_smoothing = hmc58883l_smoothing
        self.bmp085_smoothing = bmp085_smoothing


    def get_rotation_angles(self):
        return self.adxl345.getRotations(self.hmc58883l)

    def get_rotation_speeds(self):
        return self.l3g4200d.getSpeeds()

    def get_temperature(self):
        return self.bmp085.readTemperature()

    def get_pressure(self):
        self.bmp085.readTemperature()
        return self.bmp085.readPressure()

    def get_compass_direction(self):
        return self.hmc58883l.heading()

    def _get_gyro_data(self):
        return self.adxl345.getAxes(True)


copter_data_reader = CopterDataReader()

if len(sys.argv) >= 2 and sys.argv[1] == 'stat':
    print "axelX,axelY,axelZ,Temp,Pressure,Compass,GyroX,GyroY,GyroZ"
    for i in range(0, 5000):

        print ""

else:
    print "Axelerometer data:(ADXL345)"
    gyro_data = copter_data_reader._get_gyro_data()
    print "   x = %.3fG" % (gyro_data['x'])
    print "   y = %.3fG" % (gyro_data['y'])
    print "   z = %.3fG" % (gyro_data['z'])
    print "====================================="

    rotation_angles = copter_data_reader.get_rotation_angles()
    print "X: {0}; Y: {1}; Z: {2}".format(rotation_angles['x'], rotation_angles['y'], rotation_angles['z'])

    print "\nBarometer data(BMP085):"
    print "Temperature: %.2f C" % (copter_data_reader.get_temperature())
    print "Pressure:    %.2f hPa" % (copter_data_reader.get_pressure())
    print "====================================="

    print "\nGyro data(L3G4200D):"
    rotation_speeds = copter_data_reader.get_rotation_speeds()
    print "X = %.3fG " % rotation_speeds['x']
    print "Y = %.3fG " % rotation_speeds['y']
    print "Z = %.3fG " % rotation_speeds['z']

    print "\nCompass data(HMC58883l):"
    print "Heading: ", copter_data_reader.get_compass_direction()





