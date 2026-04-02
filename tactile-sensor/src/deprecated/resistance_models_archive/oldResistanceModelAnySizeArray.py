#!/usr/bin/env python

# the purpose of this script is to visualize the force on the new tactile sensor on a grid of squares

import rospy
import numpy as np
from numpy import pi
from visualization_msgs.msg import Marker
from std_msgs.msg import String
from std_msgs.msg import Float64
from serial_data.msg import resistance as res
from math import sin, cos, pi
import tf.transformations as tft
from collections import deque as deq

class grid_visualization():


    def __init__(self):
        self.m = int(input('Input # of rows: '))
        self.n = int(input('Input # of cols: '))
        self.data_in = None
        self.square_array = [[] for i in range(0,self.m)]
        self.max_R = 4000

        self.ADC_reading = np.array(np.zeros([self.m,self.n]))

        self.resistance = np.array(np.zeros([self.m,self.n]))

        self.offset = np.array(np.zeros([self.m,self.n]))

        self.force_array = np.array(np.zeros([self.m,self.n]))

        #initialize two subscribers for incoming serial data
        rospy.Subscriber('serial',String,self.callback,tcp_nodelay=False)


        while self.data_in == None:
            rospy.sleep(0.01)

        # initialize a publisher for the markers
        self.pub = rospy.Publisher('/grid_squares', Marker, queue_size = 1)
        self.rate = rospy.Rate(1000)

        # initialize a publisher for publishing the final resistance values
        self.pub_resistance = rospy.Publisher('/resistance_values', res, queue_size = 1)

        # initialize a publisher for publishing the final resistance values
        self.pub_force = rospy.Publisher('/force_values', res, queue_size = 1)

        # initialize publisher for time
        self.pub_time = rospy.Publisher('/time', Float64, queue_size = 1)

        # publisher for filtered resistance values
        self.pub_filtered = rospy.Publisher('/filtered_resistance', res, queue_size = 1)

        # publish ADC_values just for fun
        self.pub_ADC = rospy.Publisher('/raw_ADC',res,queue_size=1)

        # initialize the square markers
        for i in range(0,self.m):

            for j in range(0,self.n):

                square = Marker()
                square.header.frame_id = 'my_square'
                square.ns = 'square # ' + str(i) + ', ' + str(j)
                square.type = Marker.CUBE
                square.action = 0
                square.frame_locked = True
                square.scale.x = 0.625
                square.scale.y = 0.625
                square.scale.z = 0.125
                square.pose.position.x = i*0.625
                square.pose.position.y = j*0.625
                square.pose.position.z = 0
                square.color.r = 0.0
                square.color.g = 0.0
                square.color.b = 1.0
                square.color.a = 1.0
                square.lifetime = rospy.rostime.Duration()

                self.square_array[i].append(square)


    def callback(self,msg):
        self.data_in = msg.data
        data = np.fromstring(self.data_in, count = (self.n+1), sep = ',')
        self.ADC_reading[int(data[0])] = data[1:(self.n+1)]



    def run(self):
        Rc = 1000.0
        ADC = 1024.0 # max ADC value from Arduino

        while not rospy.is_shutdown():

            for i in range(0,self.m):
                R=[]
                for j in range(0,self.n):
                    if self.ADC_reading[i][j] < 1.0:
                        self.ADC_reading[i][j]=1.0

                    R_temp = round(-Rc*(-5.0 + (5.0/ADC)*sum((self.ADC_reading[i])))/((5.0/ADC)*self.ADC_reading[i][j]),0)
                    if R_temp >= self.max_R:
                        R_temp = self.max_R
                    R.append(R_temp)
                self.resistance[i] = np.array(R)
            # self.resistance = [self.resistance[i]+self.offset[i] for i in range(0,self.m)]

            for i in range(0,self.m):
                for j in range(0,self.n):
                    self.square_array[i][j].color.b = self.resistance[i][j]/4000
                    self.square_array[i][j].color.r = 1 - self.resistance[i][j]/4000
                    self.pub.publish(self.square_array[i][j])


            # publish the forces and resistances as a flattened matrix
            self.pub_resistance.publish(np.array(self.resistance).flatten())
            self.pub_ADC.publish(np.array(self.ADC_reading).flatten())
            self.rate.sleep()


if __name__=='__main__':

    # initializa a ROS node for the markers
    rospy.init_node('square_markers',anonymous = True)
    visualize = grid_visualization()
    visualize.run()
