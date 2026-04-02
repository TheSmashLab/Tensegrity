#!/usr/bin/env python

# Author(s): Nathan Day
# Date: January 25, 2016
# Description:
#		This script reads in data values from serial input and takes the data 100 samples at a time, adds them together then divides them by 100 to get an average value. After each average is calculated the ith location of the average array is printed to the screen and recorded in a file. Each location of the average array is printed and written to a file beginning with 1 and on through 12.

import rospy
import serial
import numpy as np
from std_msgs.msg import Float64MultiArray

def talker(usbname):
	rospy.init_node('serial_data', anonymous=True)
	pub = rospy.Publisher('/serial'+usbname, Float64MultiArray, queue_size = 1)
	# rate = rospy.Rate(10000) # 100 hz
	while not rospy.is_shutdown():
                x = Float64MultiArray()
		x.data=list(np.fromstring(reader.readline(),sep=','))
		pub.publish(x)
		# rate.sleep()

if __name__ == '__main__':
	# initialize the serial reader
	arduino = input('Input Arduino type (mega/mini): ')
        usbname = input('Enter USB name (USB0/USB1): ')

	if arduino == 'mega':
		usbPort = '/dev/ttyACM0'
		baud = '1000000'

	if arduino == 'mini':
		usbPort = '/dev/tty'+usbname
		baud = '250000'

	reader=serial.Serial(usbPort,baud)
	reader.flushInput()
	trash=reader.readline()

	try:
		talker(usbname)
	except rospy.ROSInterruptException:
		pass
