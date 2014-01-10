__author__ = 'ivanbahdanau'

# Echo client program
import socket

HOST = 'coder.local'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('10')
data = s.recv(1024)
s.close()
print 'Received', repr(data)