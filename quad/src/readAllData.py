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
print "Axelerometer data:(ADXL345)"
print "   x = %.3fG" % ( axes['x'] )
print "   y = %.3fG" % ( axes['y'] )
print "   z = %.3fG" % ( axes['z'] )
print "====================================="

print "\nBarometer data(BMP085):"
print "Temperature: %.2f C" % (bmp085.readTemperature())
print "Pressure:    %.2f hPa" % (bmp085.readPressure())
print "====================================="

print "\nCompass data(HMC58883l):"
print "Heading: " , hmc58883l.heading()
print "Degrees: " , hmc58883l.degrees(hmc58883l.heading())

print "\nGyro data(L3G4200D):"
print "X = %.3fG " % l3g4200d.getX()
print "Y = %.3fG " % l3g4200d.getY()
print "Z = %.3fG " % l3g4200d.getZ()
print "Temperature = %.3f " % l3g4200d.getTemperature()




