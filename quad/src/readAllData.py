import sys
import math

import smbus
from ADXL345 import ADXL345
from BMP085 import BMP085
from HMC58883l import HMC5883l
from L3G4200D import L3G4200D


revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

adxl345 = ADXL345(bus)
bmp085 = BMP085(bus)
hmc58883l = HMC5883l(bus)
l3g4200d = L3G4200D(bus)
axes = adxl345.getAxes(True)
rotations = adxl345.getRotations(hmc58883l)

if len(sys.argv) >= 2 and sys.argv[1] == 'stat':
    print "axelX,axelY,axelZ,Temp,Pressure,Compass,GyroX,GyroY,GyroZ"
    for i in range(0, 5000):
        axesSpeedsData = l3g4200d.getSpeeds()
        axes = adxl345.getAxes(True)
        x = axes['x']
        y = axes['y']
        z = axes['z']
        print "{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(x, y, z, bmp085.readTemperature(), bmp085.readPressure(),
                                                           hmc58883l.heading(), axesSpeedsData['x'],
                                                           axesSpeedsData['y'], axesSpeedsData['z'])
else:
    print "Axelerometer data:(ADXL345)"
    print "   x = %.3fG" % ( axes['x'] )
    print "   y = %.3fG" % ( axes['y'] )
    print "   z = %.3fG" % ( axes['z'] )
    print "====================================="

    print "X: {0}; Y: {1}; Z: {2}".format(math.degrees(rotations['x']), math.degrees(rotations['y']),
                                          math.degrees(rotations['z']))

    print "\nBarometer data(BMP085):"
    print "Temperature: %.2f C" % (bmp085.readTemperature())
    print "Pressure:    %.2f hPa" % (bmp085.readPressure())
    print "====================================="

    print "\nCompass data(HMC58883l):"
    print "Heading: ", hmc58883l.heading()
    print "Degrees: ", hmc58883l.degrees(hmc58883l.heading())

    print "\nGyro data(L3G4200D):"
    axesSpeedsData = l3g4200d.getSpeeds()
    print "X = %.3fG " % axesSpeedsData['x']
    print "Y = %.3fG " % axesSpeedsData['y']
    print "Z = %.3fG " % axesSpeedsData['z']
    print "Temperature = %.3f " % l3g4200d.getTemperature()




