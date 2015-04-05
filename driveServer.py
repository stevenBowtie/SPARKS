#!/usr/bin/python
import socket
import serial
import time

def limit(xVal):
 if 62<xVal<68:
  return 64
 else:
  return max(0,min(127,xVal))

def go(x,y):
 x=limit(x)
 y=limit(y)
 ser.write(chr(128))
 ser.write(chr(6))
 ser.write(chr(x))
 ser.write(chr((128+6+x)&0x7F))
 ser.write(chr(128))
 ser.write(chr(7))
 ser.write(chr(y))
 ser.write(chr((128+7+y)&0x7F))

#connect serial
ser=serial.Serial('/dev/ttyAMA0',38400)

#binding for single joystick
sockSingle=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockSingle.bind(('',4444))
sockSingle.setblocking(0)
singleData=0

#binding for dual joystick
sockDual=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockDual.bind(('',4445))
sockDual.setblocking(0)
dualData=0

lastSet=0
timeout=0

while 1:
#Single stick mode
 try:
  data,addr=sockSingle.recvfrom(1024)
  singleData=1
 except:
  pass
 if singleData==1:
  left=64
  right=64
  x=int(((float(0.00062*(ord(data[0])-60)**3)+0.1*ord(data[0])+120)/119)*127)
  y=127-int(((float(0.00062*(ord(data[1])-60)**3)+0.1*ord(data[1])+120)/119)*127)
  if x<64:
   left=y-(64-x)
   right=y+64-x
  else:
   left=y+x-64
   right=y-(x-64)
  print str(limit(left))+','+str(limit(right))
  go(left,right)
  singleData=0
  lastSet=time.time()
  timeout=0
#Dual stick mode
 try:
  data,addr=sockDual.recvfrom(1024)
  dualData=1
 except:
  pass
 if dualData==1:
  left=int(((float(0.000065*(ord(data[0])-127)**3)+127)/255)*127)
  right=int(((float(0.000065*(ord(data[2])-127)**3)+127)/255)*127)
  print str(limit(left))+','+str(limit(right))
  go(left,right)
  dualData=0
  lastSet=time.time()
  timeout=0
 if time.time()-lastSet>.5 and timeout!=1:
  print '64,64'
  timeout=1
  go(64,64)
