import os
import time
import math
import sys

import smbus
from ADXL345 import ADXL345
from BMP085 import BMP085
from HMC58883l import HMC5883l
from L3G4200D import L3G4200D
from MovingAverage import MovingAverage


revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

bmp085 = BMP085(bus)
hmc58883l = HMC5883l(bus)

q1MotorAddress = 4
q2MotorAddress = 3
q3MotorAddress = 1
q4MotorAddress = 0

MOTOR_STOPPED = 450

ALPHA_CONSTANT = 4

G_MATRIX = [0.5, 0.5, 0.2]

averagePeriod = 50
xRotation = MovingAverage(averagePeriod)
yRotation = MovingAverage(averagePeriod)
zRotation = MovingAverage(averagePeriod)

xAngSpeed = MovingAverage(averagePeriod)
yAngSpeed = MovingAverage(averagePeriod)
zAngSpeed = MovingAverage(averagePeriod)

flySeconds = 5
init_torque = 2000
if len(sys.argv) == 3:
    flySeconds = int(sys.argv[1])
    init_torque = int(sys.argv[2])

print "Running time:{0}; torque: {1}".format(flySeconds, init_torque)


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_rotation(x, y, z):
    return math.atan(x / dist(y, z))


def sin(angle):
    return math.sin(angle)


def cos(yRotation):
    return math.cos(yRotation)


def calculateTorques():
    # angles
    adxl345 = ADXL345(bus)
    axelerometer = adxl345.getAxes(True)
    hmc58883l = HMC5883l(bus)

    # speeds
    l3g4200d = L3G4200D(bus)

    xRotation.add(get_rotation(-1 * axelerometer['x'], axelerometer['z'], axelerometer['x']))
    yRotation.add(get_rotation(axelerometer['y'], axelerometer['x'], axelerometer['z']))
    zRotation.add(math.radians(hmc58883l.heading()))

    speedDividor = 100.

    xAngSpeed.add(l3g4200d.getX() / speedDividor)
    yAngSpeed.add(l3g4200d.getY() / speedDividor)
    zAngSpeed.add(l3g4200d.getZ() / speedDividor)

    x_vel_avg = xAngSpeed.avg()
    y_vel_avg = yAngSpeed.avg()
    z_vel_avg = zAngSpeed.avg()

    x_rotation_avg = xRotation.avg()
    y_rotation_avg = yRotation.avg()
    z_rotation_avg = zRotation.avg()

    xTorque = -1 * G_MATRIX[0] * x_vel_avg - ALPHA_CONSTANT * (
        sin(x_rotation_avg / 2) * cos(y_rotation_avg / 2) * cos(z_rotation_avg / 2) -
        cos(x_rotation_avg / 2) * sin(y_rotation_avg / 2) * sin(z_rotation_avg / 2))
    yTorque = -1 * G_MATRIX[0] * y_vel_avg - ALPHA_CONSTANT * (
        cos(x_rotation_avg / 2) * sin(y_rotation_avg / 2) * cos(z_rotation_avg / 2) +
        sin(x_rotation_avg / 2) * cos(y_rotation_avg / 2) * sin(z_rotation_avg / 2))
    zTorque = -1 * G_MATRIX[0] * z_vel_avg - ALPHA_CONSTANT * (
        cos(x_rotation_avg / 2) * cos(y_rotation_avg / 2) * sin(z_rotation_avg / 2) -
        sin(x_rotation_avg / 2) * sin(y_rotation_avg / 2) * cos(z_rotation_avg / 2))

    # print 'R, {0}, {1}, {2}, S, {3}, {4}, {5}, T, {6}, {7}, {8}'.format(xRotation, yRotation, zRotation,
    # xSpeed, ySpeed,
    #
    # zSpeed, xTorque, yTorque, zTorque)
    return [xTorque, yTorque, zTorque, x_rotation_avg, y_rotation_avg, z_rotation_avg, x_vel_avg, y_vel_avg, z_vel_avg]


def calculateMotorSpeeds(torques, T):
    a1, a2, a3 = 62695.9247649, 227272.72727272727, 8620.690
    t1, t2, t3 = torques[0], torques[1], torques[2]
    constantDesiredTorque = T * a3
    w1 = max(t2 * a1 + t3 * a2 + constantDesiredTorque, 0)
    w2 = max(t1 * a1 - t3 * a2 + constantDesiredTorque, 0)
    w3 = max(- t2 * a1 + t3 * a2 + constantDesiredTorque, 0)
    w4 = max(- t1 * a1 - t3 * a2 + constantDesiredTorque, 0)

    # print " {0},{1},{2},{3}".format(math.sqrt(w1), math.sqrt(w2), math.sqrt(w3), math.sqrt(w4))
    return [math.sqrt(w1), math.sqrt(w2), math.sqrt(w3), math.sqrt(w4)]


def runMotors(q1, q3, q2, q4):
    os.system(
        "echo {0}={1} > /dev/servoblaster;"
        "echo {2}={3} > /dev/servoblaster;"
        "echo {4}={5} > /dev/servoblaster;"
        "echo {6}={7} > /dev/servoblaster;".format(int(q1MotorAddress), int(q1),
                                                   int(q2MotorAddress), int(q2),
                                                   int(q3MotorAddress), int(q3),
                                                   int(q4MotorAddress), int(q4)))


millis = int(round(time.time() * 1000))

torques = calculateTorques()
motorSpeeds = calculateMotorSpeeds(torques, init_torque)
q1 = MOTOR_STOPPED + int(motorSpeeds[0])
q2 = MOTOR_STOPPED + int(motorSpeeds[1])
q3 = MOTOR_STOPPED + int(motorSpeeds[2])
q4 = MOTOR_STOPPED + int(motorSpeeds[3])
print " {0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}".format(q1, q3, q2, q4, torques[0], torques[1],
                                                                       torques[2], torques[3], torques[4],
                                                                       torques[5], torques[6], torques[7],
                                                                       torques[8])
while millis + flySeconds * 1000 > int(round(time.time() * 1000)):
    torques = calculateTorques()
    motorSpeeds = calculateMotorSpeeds(torques, init_torque)
    adjusted = 2350
    q1 = MOTOR_STOPPED + int(motorSpeeds[0] - adjusted) / 5
    q2 = MOTOR_STOPPED + int(motorSpeeds[1] - adjusted) / 5
    q3 = MOTOR_STOPPED + int(motorSpeeds[2] - adjusted) / 5
    q4 = MOTOR_STOPPED + int(motorSpeeds[3] - adjusted) / 5
    print " {0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}".format(q1, q3, q2, q4, torques[0], torques[1],
                                                                           torques[2], torques[3], torques[4],
                                                                           torques[5], torques[6], torques[7],
                                                                           torques[8])
    runMotors(q1, q3, q2, q4)
else:
    runMotors(MOTOR_STOPPED, MOTOR_STOPPED, MOTOR_STOPPED, MOTOR_STOPPED)
    print "done"
