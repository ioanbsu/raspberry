__author__ = 'ivanbahdanau'

import RPi.GPIO as gpio
import os
import socket

gpio.setmode(gpio.BOARD)
gpio.setup(12,gpio.OUT)
gpio.output(12,False)

HOST = ''                 # Symbolic name meaning the local host
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

while 1:
    print 'Connected by', addr
    data = conn.recv(1024)
    print data
    if not data:
        break
    if data:
        if data == 'up':
            os.system('echo 1=+10 > /dev/servoblaster')
        if data == 'down':
            os.system('echo 1=-10 > /dev/servoblaster')
        if data == 'stop':
            os.system('echo 1=20% > /dev/servoblaster')
        if data == 'max':
            os.system('echo 1=100% > /dev/servoblaster')
        print data
        gpio.output(12, True)
    else:
        gpio.output(12, False)
conn.close()