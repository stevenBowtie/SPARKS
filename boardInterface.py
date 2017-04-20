#!/usr/bin/python
import sys
import cwiid
import sys
from time import sleep
import socket

threshold=200

def main():
	global wiimote
	def init_remote():
		global wiimote
		global named_calibration
		while 1:
			try:
				wiimote = cwiid.Wiimote()
				sleep(1)
				if wiimote:
					print 'Wiimote found'
					break
			except(KeyboardInterrupt):
				break
			except:
				pass
		wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
		wiimote.led=1
		wiimote.request_status()
		balance_calibration = wiimote.get_balance_cal()
		named_calibration = { 'right_top': balance_calibration[0],
								'right_bottom': balance_calibration[1],
								'left_top': balance_calibration[2],
								'left_bottom': balance_calibration[3],
							}
		return wiimote

	def sensor_read():
		wiimote.request_status()
		readings=wiimote.state['balance']
		data=[]
		for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
			reading = readings[sensor]
			calibration = named_calibration[sensor]
			if reading < calibration[1]:
				reading=(1700*(reading - calibration[0]) / (calibration[1] - calibration[0]))
			else:
				reading=(1700*(reading - calibration[1]) / (calibration[2] - calibration[1])+1700)
			if reading<threshold:
				reading=0
			reading=max(0,reading)
			data.append(reading)
		total_load=1
		for reading in data:
		  total_load+=reading
		output=[]
		for reading in data:
			output.append(reading*100/total_load)
		if total_load<threshold:
			output=[25,25,25,25]
		return output

	def translate_lr(input):
		right=(input[0]-input[2])/50.0
		left=(input[1]-input[3])/50.0
		return (left,right)
		
	def scale_for_motor(value):
		value = max(-1.0, min(1.0, value))
		return max(0,min(512,int(value*64 + 64)*1.5-32))
	
	def accel(target,current):
		x=(target[0]-current[0])*.1+current[0]
		y=(target[1]-current[1])*.1+current[1]
		return [int(x),int(y)]

	sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	prev_coords=[64,64]
	ride=0
	notify=0
	while 1:
		init_remote()
		while 1:
			try:
				wiimote.request_status()
				if wiimote.state['buttons']:
					ride=1
					notify=0
					state=0
					for x in range(6):
						wiimote.led=state
						state=not state
						sleep(.5)
				if ride:
					coords=[scale_for_motor(v) for v in translate_lr(sensor_read())]
					coords=accel(coords,prev_coords);
					prev_coords=coords
					mesg=chr(coords[0])+chr(coords[1])
					print sock
					result=sock.sendto(mesg, '/tmp/driveSocket')
					sleep(0.025)
				if sensor_read()==[25,25,25,25]:
					ride=0
					if not notify:
						mesg=chr(64)+chr(64)
						#sock.sendto(mesg, '/tmp/driveSocket')
						print 'Rider lost'
						notify=1
			except(RuntimeError):
				print RuntimeError
				mesg=chr(64)+chr(64)
				sock.sendto(mesg, '/tmp/driveSocket')
				print 'Lost connection'
				exit()
			except(KeyboardInterrupt):
				break
			except:
				exit()
main()
