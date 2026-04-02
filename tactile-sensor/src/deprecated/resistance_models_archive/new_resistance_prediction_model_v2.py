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
import pdb

class grid_visualization():


    def __init__(self):

        self.m = int(input('Insert # of Rows: '))
        self.n = int(input('Insert # of Cols: '))

        self.data_in = None

        self.square_array = [[] for i in range(0,self.m)]

        self.ADC_reading = np.array(np.zeros([self.m,self.n]))

        self.resistance = np.array(np.zeros([self.m,self.n]))

        self.offset = np.array(np.zeros([self.m,self.n]))

        self.force_array = np.array(np.zeros([self.m,self.n]))

        #initialize two subscribers for incoming serial data
        rospy.Subscriber('serial',String,self.callback,tcp_nodelay=False)


        while self.data_in == None:
            rospy.sleep(0.01)

        # initialize a publisher for the markers
        self.pub = rospy.Publisher('/grid_squares_new', Marker, queue_size = 1)
        self.rate = rospy.Rate(1000)

        # initialize a publisher for publishing the final resistance values
        self.pub_resistance = rospy.Publisher('/resistance_values_new', res, queue_size = 1)


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
                # square.pose.position.x = 2.66*cos(j*2*pi/27)
                # square.pose.position.y = 2.66*sin(j*2*pi/27)
                # square.pose.position.z = -i*0.625
                # square.pose.orientation.x = quat[0]
                # square.pose.orientation.y = quat[1]
                # square.pose.orientation.z = quat[2]
                # square.pose.orientation.w = quat[3]
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
        ADC = 1024.0 # max reading of ADC on Arduino (i.e 1024 or 256)
        p = self.m*self.n # size of block matrix
        # R = [[330.0],[1000.0],[2200.0]] # constant resistor value
        R = 330.0
        vout_mat = np.empty((self.m, self.n, self.n))
        Ic_temp = np.empty((self.m,self.n))

        while not rospy.is_shutdown():

            # pdb.set_trace()


            voltage = self.ADC_reading

            vout_mat = [ADC*np.identity(self.n)-(np.ones((self.n, self.n))*voltage[i]).T for i in range(0, self.m)]

            block_mat = block(*vout_mat)


            Ic_temp = [voltage[i]/R for i in range(0,self.m)]

            Ic = np.reshape(Ic_temp,(self.m*self.n,1))


            R_inverted = slv(block_mat,Ic)

            R_predicted = 1./R_inverted

            for i in range(0,len(R_predicted)):
                if R_predicted[i]>4000.0:
                    R_predicted[i] = 4000.0

            R_reshaped = np.reshape(R_predicted,(self.m,self.n))

            for i in range(0,self.m):
                for j in range(0,self.n):
                    self.square_array[i][j].color.b = R_reshaped[i][j]/4000
                    self.square_array[i][j].color.r = 1 - R_reshaped[i][j]/4000
                    # self.square_array[i][j].pose.position.x = j*0.625
                    # self.square_array[i][j].pose.position.y = i*0.625
                    self.pub.publish(self.square_array[i][j])

            # publish the forces and resistances as a flattened matrix
            self.pub_resistance.publish(R_predicted)
            # self.rate.sleep()


if __name__=='__main__':

    # initializa a ROS node for the markers
    rospy.init_node('square_markers_new',anonymous = True)
    visualize = grid_visualization()
    visualize.run()
