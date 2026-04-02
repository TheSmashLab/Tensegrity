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

class grid_visualization():


    def __init__(self):

        self.data_in = None

        self.square_array = [[],[],[],[],[],[],[],[],[],[],[]]

        self.ADC_reading = np.array(np.zeros([11,27]))

        self.resistance = np.array(np.zeros([11,27]))

        self.offset = np.array(np.zeros([11,27]))

        self.force_array = np.array(np.zeros([11,27]))

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
        for i in range(0,11):

            for j in range(0,27):

                R_z = np.matrix([[cos(-j*2*pi/27),sin(-j*2*pi/27),0,0],[-sin(-j*2*pi/27),cos(-j*2*pi/27),0,0],[0,0,1,0],[0,0,0,1]])
                R_y = np.matrix([[cos(pi/2),0,-sin(pi/2),0],[0,1,0,0],[sin(pi/2),0,cos(pi/2),0],[0,0,0,1]])
                R_matrix = R_z*R_y
                quat = tft.quaternion_from_matrix(R_matrix)

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
                # self.square.pose.position.x = 2.66*cos(j*2*pi/27)
                # self.square.pose.position.y = 2.66*sin(j*2*pi/27)
                # self.square.pose.position.z = -i*0.625
                # self.square.pose.orientation.x = quat[0]
                # self.square.pose.orientation.y = quat[1]
                # self.square.pose.orientation.z = quat[2]
                # self.square.pose.orientation.w = quat[3]
                self.square.color.r = 0.0
                self.square.color.g = 0.0
                self.square.color.b = 1.0
                self.square.color.a = 1.0
                self.square.lifetime = rospy.rostime.Duration()

                self.square_array[i].append(self.square)



    def callback(self,msg):
        self.data_in = msg.data
        data = np.fromstring(self.data_in, count = 28, sep = ',')
        self.ADC_reading[data[0]] = data[1:28]



    def run(self):
        m = len(self.ADC_reading)# number of rows
        n = len(self.ADC_reading[0])# number of cols
        p = m*n # size of block matrix
        R = 56000.0 # constant resistor value
        col_current = np.zeros([1,n])
        row_current = np.zeros([1,m])
        vout_mat = np.zeros([p,p])

        while not rospy.is_shutdown():

            voltage = self.ADC_reading*5.0/256.0

            vout_mat_0 = (np.ones((n,n))*voltage[0]).T
            vout_mat_1 = (np.ones((n,n))*voltage[1]).T
            vout_mat_2 = (np.ones((n,n))*voltage[2]).T
            vout_mat_3 = (np.ones((n,n))*voltage[3]).T
            vout_mat_4 = (np.ones((n,n))*voltage[4]).T
            vout_mat_5 = (np.ones((n,n))*voltage[5]).T
            vout_mat_6 = (np.ones((n,n))*voltage[6]).T
            vout_mat_7 = (np.ones((n,n))*voltage[7]).T
            vout_mat_8 = (np.ones((n,n))*voltage[8]).T
            vout_mat_9 = (np.ones((n,n))*voltage[9]).T
            vout_mat_10 = (np.ones((n,n))*voltage[10]).T

           # print 5*np.identity(n)-vout_mat_0

            block_mat = block(5*np.identity(n)-vout_mat_0,
                              5*np.identity(n)-vout_mat_1,
                              5*np.identity(n)-vout_mat_2,
                              5*np.identity(n)-vout_mat_3,
                              5*np.identity(n)-vout_mat_4,
                              5*np.identity(n)-vout_mat_5,
                              5*np.identity(n)-vout_mat_6,
                              5*np.identity(n)-vout_mat_7,
                              5*np.identity(n)-vout_mat_8,
                              5*np.identity(n)-vout_mat_9,
                              5*np.identity(n)-vout_mat_10)


            Ic = np.array(np.concatenate((voltage[0]/R,
                           voltage[1]/R,
                           voltage[2]/R,
                           voltage[3]/R,
                           voltage[4]/R,
                           voltage[5]/R,
                           voltage[6]/R,
                           voltage[7]/R,
                           voltage[8]/R,
                           voltage[9]/R,
                                          voltage[10]/R),axis=0))

            R_inverted = slv(block_mat,Ic)

            R_predicted = 1./R_inverted

            # for i in range(0,len(R_predicted)):
            #     if R_predicted[i]>4000.0:
            #         R_predicted[i] = 4000.0

            # print R_predicted

            R_reshaped = R_predicted.reshape(m,n)

            for i in range(0,n):
                # print block_mat[i*n+1][i*n+1]
                # print R_reshaped[i][0]
                col_current[0][i] = block_mat[i][i]/R_reshaped[0][i]

            for i in range(0,m):
                row_current[0][i] = block_mat[i*n+1][i*n+1]/R_reshaped[i][0]

            print('total row current = ',sum(row_current[0]))
            print('total column current = ',sum(col_current[0]))
            # print R_reshaped

            for i in range(0,11):
                for j in range(0,27):
                    self.square_array[i][j].color.b = R_reshaped[i][j]/4000
                    self.square_array[i][j].color.r = 1 - R_reshaped[i][j]/4000
                    # self.square_array[i][j].scale.z = 1.0/(2*(R_reshaped[i][j]/4000))
                    # # self.square_array[i][j].pose.position.z = 1.0/(R_reshaped[i][j]/4000)
                    # self.square_array[i][j].pose.position.x = 2.66*cos(j*2*pi/27)+(1.0/(2*(R_reshaped[i][j]/4000))*cos(j*2*pi/27))/2.0
                    # self.square_array[i][j].pose.position.y = 2.66*sin(j*2*pi/27)+(1.0/(2*(R_reshaped[i][j]/4000))*sin(j*2*pi/27))/2.0
                    self.pub.publish(self.square_array[i][j])

            # publish the forces and resistances as a flattened matrix
            self.pub_resistance.publish(R_predicted)
            # self.rate.sleep()


if __name__=='__main__':

    # initializa a ROS node for the markers
    rospy.init_node('square_markers_new',anonymous = True)
    visualize = grid_visualization()
    visualize.run()
