import os
import time
import math
import sys

from myQuad import CopterDataReader


q1MotorAddress = 4
q2MotorAddress = 3
q3MotorAddress = 1
q4MotorAddress = 0

MOTOR_STOPPED = 450

ALPHA_CONSTANT = 4

G_MATRIX = [0.5, 0.5, 0.2]

averagePeriod = 20
flySeconds = 5
init_torque = 200
if len(sys.argv) == 3:
    flySeconds = int(sys.argv[1])
    init_torque = int(sys.argv[2])

print "Running time:{0}; torque: {1}".format(flySeconds, init_torque)


copter_data_reader = CopterDataReader()

def sin(angle):
    return math.sin(angle)


def cos(yRotation):
    return math.cos(yRotation)


def calculateTorques(rotations,ang_speeds):
    # speeds
    xRotation.add(rotations['x'])
    yRotation.add(rotations['y'])
    zRotation.add(rotations['z'])

    speedDividor = 100.

    xAngSpeed.add(ang_speeds['x'])
    yAngSpeed.add(ang_speeds['y'])
    zAngSpeed.add(ang_speeds['z'])

    x_vel_avg = xAngSpeed.avg() / speedDividor
    y_vel_avg = yAngSpeed.avg() / speedDividor
    z_vel_avg = zAngSpeed.avg() / speedDividor

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
    return [xTorque, yTorque, zTorque]


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

while millis + flySeconds * 1000 > int(round(time.time() * 1000)):
    adxl345 = ADXL345(bus)
    rotations=adxl345.getRotations(hmc58883l)
    l3g4200d = L3G4200D(bus)
    ang_speeds = l3g4200d.getSpeeds()

    torques = calculateTorques(rotations,ang_speeds)
    motorSpeeds = calculateMotorSpeeds(torques, init_torque)
    adjusted = 2350
    q1 = MOTOR_STOPPED + int(motorSpeeds[0] - adjusted) / 5
    q2 = MOTOR_STOPPED + int(motorSpeeds[1] - adjusted) / 5
    q3 = MOTOR_STOPPED + int(motorSpeeds[2] - adjusted) / 5
    q4 = MOTOR_STOPPED + int(motorSpeeds[3] - adjusted) / 5
    print " {0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}".format(q1, q3, q2, q4,
                                                                           torques[0], torques[1],torques[2],
                                                                           rotations['x'],rotations['y'],rotations['z'],
                                                                           ang_speeds['x'],ang_speeds['y'],ang_speeds['z'])
    runMotors(q1, q3, q2, q4)
else:
    runMotors(MOTOR_STOPPED, MOTOR_STOPPED, MOTOR_STOPPED, MOTOR_STOPPED)