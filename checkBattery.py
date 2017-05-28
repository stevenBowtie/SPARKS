#!/usr/bin/python
import serial
from time import sleep
ser=serial.Serial('/dev/ttyAMA0',38400)
ser.flush()
ser.write(chr(0x80))
ser.write(chr(24)) #24
sleep(.5)
print ord(ser.read())
print ord(ser.read())
#voltage=int(ser.read())/10.0
#print voltage
ser.close()
exit()
