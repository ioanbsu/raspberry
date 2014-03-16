# ADXL345 Python example
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
#
# This is an example to show you how to use our ADXL345 Python library
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer
import smbus

import ADXL345
import BMP085
from HMC58883l import HMC5883l

# select the correct i2c bus for this revision of Raspberry Pi
import L3G4200D

revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

adxl345 = ADXL345(bus)
bmp085 = BMP085(bus)
hmc58883l = HMC5883l(bus)
l3g4200d = L3G4200D(bus)

axes = adxl345.getAxes(True)
print "Axelerometer data:"
print "   x = %.3fG" % ( axes['x'] )
print "   y = %.3fG" % ( axes['y'] )
print "   z = %.3fG" % ( axes['z'] )
print "====================================="

print "\nBarometer data:"
print "Temperature: %.2f C" % (bmp085.readTemperature())
print "Pressure:    %.2f hPa" % (bmp085.readPressure())
print "====================================="

print "\nCompass data:"
print "Heading: " , hmc58883l.heading()
print "Degrees: " , hmc58883l.degrees(hmc58883l.heading())

print "\nGyro data:"
print "X = %.3fG " % l3g4200d.getX()
print "Y = %.3fG " % l3g4200d.getY()
print "Z = %.3fG " % l3g4200d.getZ()
print "Temperature = %.3f " % l3g4200d.getTemperature()



