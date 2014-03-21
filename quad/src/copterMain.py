import os
import time
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

redMotor1 = 3
redMotor2 = 0
blackMotor1 = 4
blackMotor2 = 1

MOTOR_STOPPED = 250
MOTOR_START_SPEED = 300

MIN_TEST_SPEED = 297
MAX_TEST_SPEED = 325
MAX_ROTATE_SPEED = 25
BALANCE_ROTATION = 15
MAX_MOTORS_DELTA = MAX_TEST_SPEED - MIN_TEST_SPEED

initCompassPosition = hmc58883l.heading()


def runMotors(redMotor1Speed, redMotor2Speed, blackMotor1Speed, blackMotor2Speed):
    os.system(
        "echo {0}={1} > /dev/servoblaster;"
        "echo {2}={3} > /dev/servoblaster;"
        "echo {4}={5} > /dev/servoblaster;"
        "echo {6}={7} > /dev/servoblaster;".format(int(redMotor1), int(redMotor1Speed),
                                                   int(redMotor2), int(redMotor2Speed),
                                                   int(blackMotor1), int(blackMotor1Speed),
                                                   int(blackMotor2), int(blackMotor2Speed)))
    # time.sleep(0.5)


def testMotor(motor):
    os.system("echo {0}={1} > /dev/servoblaster".format(motor, MOTOR_START_SPEED))
    time.sleep(1)
    os.system("echo {0}={1} > /dev/servoblaster".format(motor, MOTOR_STOPPED))


millis = int(round(time.time() * 1000))
print millis

redMotorSpeed = MOTOR_START_SPEED
blackMotorSpeed = MOTOR_START_SPEED
turnSpeed = 1

lastAdjusted = 0
print initCompassPosition
while millis + 40000 > int(round(time.time() * 1000)):
    runMotors(redMotorSpeed, redMotorSpeed, blackMotorSpeed, blackMotorSpeed)
    currentCompassPosition = hmc58883l.heading()
    angleDelta1 = math.fabs(initCompassPosition - currentCompassPosition)
    angleDelta2 = math.fabs(360 - angleDelta1)

    zRotation = l3g4200d.getZ()

    goingLeft = (angleDelta1 < angleDelta2 and currentCompassPosition > initCompassPosition) \
                or ( angleDelta1 > angleDelta2 and currentCompassPosition < initCompassPosition)

    rotateAngle = math.fabs(min(angleDelta1, angleDelta2))
    addAngleValue = rotateAngle * 1.
    if goingLeft:
        redMotorSpeed = (redMotorSpeed + blackMotorSpeed - addAngleValue) / 2.
        blackMotorSpeed = (redMotorSpeed + blackMotorSpeed + addAngleValue) / 2.
    else:
        redMotorSpeed = (redMotorSpeed + blackMotorSpeed + addAngleValue) / 2.
        blackMotorSpeed = (redMotorSpeed + blackMotorSpeed - addAngleValue) / 2.

    while math.fabs(blackMotorSpeed - redMotorSpeed) > MAX_MOTORS_DELTA:
        if redMotorSpeed < blackMotorSpeed:
            redMotorSpeed += 1
            blackMotorSpeed -= 1
        else:
            redMotorSpeed -= 1
            blackMotorSpeed += 1

    # else:
    # redMotorSpeed = int((redMotorSpeed + blackMotorSpeed) / 2.)
    # blackMotorSpeed = int(((redMotorSpeed + blackMotorSpeed) / 2.))

    if redMotorSpeed > MAX_TEST_SPEED:
        redMotorSpeed = MAX_TEST_SPEED
    if blackMotorSpeed > MAX_TEST_SPEED:
        blackMotorSpeed = MAX_TEST_SPEED
    if redMotorSpeed < MIN_TEST_SPEED:
        redMotorSpeed = MIN_TEST_SPEED
    if blackMotorSpeed < MIN_TEST_SPEED:
        blackMotorSpeed = MIN_TEST_SPEED

    direction = ""
    if goingLeft:
        direction = "going left"
    else:
        direction = "going right"

    print "d:{0}   a:{1}   c:{2}   a1:{3} a2:{4}   mr:{5} mb:{6}" \
        .format(direction, addAngleValue, currentCompassPosition, angleDelta1, angleDelta2,
                redMotorSpeed, blackMotorSpeed)

else:
    os.system(
        "echo {0}={1} > /dev/servoblaster;"
        "echo {2}={3} > /dev/servoblaster;"
        "echo {4}={5} > /dev/servoblaster;"
        "echo {6}={7} > /dev/servoblaster;".format(redMotor1, MOTOR_STOPPED,
                                                   redMotor2, MOTOR_STOPPED,
                                                   blackMotor1, MOTOR_STOPPED,
                                                   blackMotor2, MOTOR_STOPPED))

    # testMotor(redMotor1)
    # testMotor(redMotor2)
    #
    # testMotor(blackMotor1)
    # testMotor(blackMotor2)