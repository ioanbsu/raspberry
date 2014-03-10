__author__ = 'ivanbahdanau'

import RPi.GPIO as gpio
import time
import socket

gpio.setmode(gpio.BOARD)
gpio.setup(7,gpio.OUT)
gpio.setup(11,gpio.OUT)
gpio.setup(13,gpio.OUT)
gpio.setup(15,gpio.OUT)

gpio.output(7,True)
gpio.output(11,True)

HOST = ''                 # Symbolic name meaning the local host
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
while 1:
    data = conn.recv(1024)
    if not data: break
    for x in range(0,int(data)):
        print "turning on"
        gpio.output(13,True)
        gpio.output(15,False)
        time.sleep(1)
        print "turning off"
        gpio.output(13,False)
        gpio.output(15,True)
        time.sleep(1)
    conn.send(data)
conn.close()