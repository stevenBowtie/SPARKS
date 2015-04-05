#!/usr/bin/python
import serial
from time import sleep
con=serial.Serial('/dev/ttyAMA0',38400)
con.write(chr(128)+chr(24))
sleep(1)
data=con.read(con.inWaiting())
print str(ord(data[1])/10.0)+'V'
con.close()
