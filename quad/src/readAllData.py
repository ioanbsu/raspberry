import sys
import math

import smbus
from ADXL345 import ADXL345
from BMP085 import BMP085
from HMC58883l import HMC5883l
from L3G4200D import L3G4200D
from MovingAverage import MovingAverage


revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

adxl345 = ADXL345(bus)
bmp085 = BMP085(bus)
hmc58883l = HMC5883l(bus)
l3g4200d = L3G4200D(bus)
axes = adxl345.getAxes(True)


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_rotation(x, y, z):
    radians = math.atan(x / dist(y, z))
    return radians


if len(sys.argv) >= 2 and sys.argv[1] == 'stat':
    gx = MovingAverage(100)
    gy = MovingAverage(100)
    gz = MovingAverage(100)
    for i in range(0, 5000):
        axes = adxl345.getAxes(True)
        x = axes['x']
        y = axes['y']
        z = axes['z']
        gx.add(x)
        gy.add(y)
        gz.add(z)
        print "{0},{1},{2},{3},{4},{5}".format(x, y, z, gx.avg(), gy.avg(),
                                               gz.avg())
else:
    print "Axelerometer data:(ADXL345)"
    print "   x = %.3fG" % ( axes['x'] )
    print "   y = %.3fG" % ( axes['y'] )
    print "   z = %.3fG" % ( axes['z'] )
    print "====================================="

    xRotation = get_rotation(-1 * axes['y'], axes['z'], axes['x'])
    yRotation = get_rotation(axes['x'], axes['y'], axes['z'])
    zRotation = hmc58883l.heading()
    print "X: {0}; Y: {1}; Z: {2}".format(xRotation, yRotation, math.radians(zRotation))

    print "\nBarometer data(BMP085):"
    print "Temperature: %.2f C" % (bmp085.readTemperature())
    print "Pressure:    %.2f hPa" % (bmp085.readPressure())
    print "====================================="

    print "\nCompass data(HMC58883l):"
    print "Heading: ", hmc58883l.heading()
    print "Degrees: ", hmc58883l.degrees(hmc58883l.heading())

    print "\nGyro data(L3G4200D):"
    print "X = %.3fG " % l3g4200d.getX()
    print "Y = %.3fG " % l3g4200d.getY()
    print "Z = %.3fG " % l3g4200d.getZ()
    print "Temperature = %.3f " % l3g4200d.getTemperature()




