#!/usr/bin/python
import math

import web
import smbus
from ADXL345 import ADXL345
from MovingAverage import MovingAverage

MOVINGAVERAGESIZE = 20

urls = (
'/', 'index'
)
revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)
adxl345 = ADXL345(bus)

averageX=MovingAverage(MOVINGAVERAGESIZE)
averageY=MovingAverage(MOVINGAVERAGESIZE)

class index:
    def GET(self):
        axes = adxl345.getAxes(True)
        averageX.add(axes['x'])
        averageY.add(axes['y'])
        return str(math.degrees(averageX.avg())) + " " + str(math.degrees(averageY.avg()))


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

