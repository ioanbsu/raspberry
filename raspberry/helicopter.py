__author__ = 'ivanbahdanau'

import socket
import time
import sys

import RPi.GPIO as gpio


def configure_gpio():
    gpio.setmode(gpio.BOARD)
    gpio.setup(12, gpio.OUT)
    gpio.setup(16, gpio.OUT)
    gpio.setup(18, gpio.OUT)
    gpio.setup(22, gpio.OUT)
    gpio.setup(7, gpio.OUT)
    gpio.setup(11, gpio.OUT)
    gpio.setup(13, gpio.OUT)
    gpio.setup(15, gpio.OUT)
    gpio.output(12, False)
    gpio.output(16, False)
    gpio.output(18, False)
    gpio.output(22, False)
    gpio.output(7, True)
    gpio.output(11, True)





def state0():
    gpio.output(12, False)
    gpio.output(16, False)
    gpio.output(18, False)
    gpio.output(22, False)

def state1():
    gpio.output(12, True)
    gpio.output(16, False)
    gpio.output(18, False)
    gpio.output(22, True)


def state2():
    gpio.output(12, True)
    gpio.output(16, True)
    gpio.output(18, False)
    gpio.output(22, False)


def state3():
    gpio.output(12, False)
    gpio.output(16, True)
    gpio.output(18, False)
    gpio.output(22, False)


def state4():
    gpio.output(12, False)
    gpio.output(16, True)
    gpio.output(18, True)
    gpio.output(22, False)


def state5():
    gpio.output(12, False)
    gpio.output(16, False)
    gpio.output(18, True)
    gpio.output(22, False)


def state6():
    gpio.output(12, False)
    gpio.output(16, False)
    gpio.output(18, True)
    gpio.output(22, False)


def state7():
    gpio.output(12, False)
    gpio.output(16, False)
    gpio.output(18, True)
    gpio.output(22, True)


def state8():
    gpio.output(12, False)
    gpio.output(16, False)
    gpio.output(18, False)
    gpio.output(22, True)


def establish_connection_listener():
    global socksize, HOST, PORT, s, conn, addr, data
    socksize = 1024
    HOST = ''                 # Symbolic name meaning the local host
    PORT = 50007              # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    try:
        while True:
            conn, addr = s.accept()
            print("Now listening...\n")
            print 'New connection from %s:%d' % (addr[0], addr[1])
            data = conn.recv(socksize)
            if not data:
                break
            elif data == 'killsrv':
                conn.close()
                sys.exit()
            elif data=='motor':
                rotate_motor()
            elif data=='light':
                light_signal()
                conn.close()
            gpio.output(13, False)
            gpio.output(15, False)
    finally:
        conn.close()


def light_signal():
    global x
    print "turning on"
    gpio.output(13, True)
    gpio.output(15, False)
    time.sleep(0.1)
    print "turning off"
    gpio.output(13, False)
    gpio.output(15, True)
    time.sleep(0.1)

def rotate_motor():
    global delay, x
    delay = 0.001
    for x in range(0, 100):
        state8()
        time.sleep(delay)
        state7()
        time.sleep(delay)
        state6()
        time.sleep(delay)
        state5()
        time.sleep(delay)
        state4()
        time.sleep(delay)
        state3()
        time.sleep(delay)
        state2()
        time.sleep(delay)
        state1()
        time.sleep(delay)


configure_gpio()
state0()
establish_connection_listener()




