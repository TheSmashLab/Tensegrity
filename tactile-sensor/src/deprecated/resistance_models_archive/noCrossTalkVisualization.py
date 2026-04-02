#!/usr/bin/env python
import rospy
import numpy as np
from numpy import pi
from visualization_msgs.msg import Marker
from std_msgs.msg import String
from std_msgs.msg import Float64
from serial_data.msg import resistance as res
from math import sin, cos, pi, sqrt
import tf.transformations as tft
from collections import deque as deq
from scipy.linalg import block_diag as block
from scipy.linalg import solve as slv

class noCrossTalk():

	def __init__(self):

		self.m = int(input('Please enter # of rows: '))
		self.n = int(input('Please enter # of columns: '))

		self.data_in = None

		# self.square_array = [[],[],[],[],[],[],[],[],[],[],[]]
		self.square_array = []
		for item in range(0,self.m):
			self.square_array.append([])

		self.ADC_reading = np.array(np.zeros([self.m,self.n]))

		#initialize two subscribers for incoming serial data
		rospy.Subscriber('serial',String,self.callback,tcp_nodelay=False)


		while self.data_in == None:
		    rospy.sleep(0.01)

		# initialize a publisher for the markers
		self.pub = rospy.Publisher('/grid_squares_new', Marker, queue_size = 1)
		self.rate = rospy.Rate(1000)        

		# initialize the square markers
		for i in range(0,self.m):

			for j in range(0,self.n):


				self.square = Marker()
				self.square.header.frame_id = 'my_square'
				self.square.ns = 'square # ' + str(i) + ', ' + str(j)
				self.square.type = Marker.CUBE
				self.square.action = 0
				self.square.frame_locked = True
				self.square.scale.x = 0.625
				self.square.scale.y = 0.625
				self.square.scale.z = 0.125
				self.square.pose.position.x = i*0.625
				self.square.pose.position.y = j*0.625
				self.square.pose.position.z = 0
				self.square.color.r = 0.0
				self.square.color.g = 0.0
				self.square.color.b = 1.0
				self.square.color.a = 1.0
				self.square.lifetime = rospy.rostime.Duration()

				self.square_array[i].append(self.square)


	def callback(self,msg):
		self.data_in = msg.data
		data_array= np.fromstring(self.data_in, count = (self.n+1), sep = ',')
		self.ADC_reading[int(data_array[0])] = data_array[1:(self.n+1)]


	def run(self):
		
		offset = np.array(np.zeros((self.m,self.n)))
		# rospy.sleep(.1)
		# for k in range(0,10):
		# 	offset = self.ADC_reading + offset
		# 	rospy.sleep(.1)

		# offset = offset/10.0

		while not rospy.is_shutdown():
			for i in range(0,self.m):
				for j in range(0,self.n):

					self.square_array[i][j].color.b = 1-(self.ADC_reading[i][j]-offset[i][j])/256.0
					self.square_array[i][j].color.r = (self.ADC_reading[i][j]-offset[i][j])/256.0
					if self.ADC_reading[i][j]==0:
						self.ADC_reading[i][j]=1.0
					# self.square_array[i][j].pose.position.z = 1.0/(R_reshaped[i][j]/4000)
					self.pub.publish(self.square_array[i][j])


if __name__=='__main__':
    
    # initializa a ROS node for the markers
    rospy.init_node('square_markers_new',anonymous = True)
    visualize = noCrossTalk()
    visualize.run()