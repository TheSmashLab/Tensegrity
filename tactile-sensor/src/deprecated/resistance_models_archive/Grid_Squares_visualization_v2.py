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
        # initialize an array of zeros to be used to size ADC_reading and resitance dictionaries
        zeros_27 = np.array([0 for i in range(0,27)])

        self.data_in = None
        self.square_array = [[],[],[],[],[],[],[],[],[],[],[]]
        self.t0 = round(rospy.get_time(),5)
        self.dt = deq([0,0.012],maxlen=2)
        self.max_R = 4000
               
        self.ADC_reading = np.array(np.zeros([11,27]))
        
        self.resistance = np.array(np.zeros([11,27]))

        self.offset = np.array(np.zeros([11,27]))

        self.force_array = np.array(np.zeros([11,27]))

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
      
        # take 100 samples of each value in order to take an average
        for h in range(0,100):
            for i in range(0,11):
                R=[]
                for j in range(0,27):
                    if self.ADC_reading[i][j] < 1.0:
                        self.ADC_reading[i][j]=1.0
                    R_temp = round(-2200.0*(-5.0 + (5.0/256)*sum((self.ADC_reading[i])))/((5.0/256)*self.ADC_reading[i][j]),0)
                    
                    # if the resistance value is greater than max_R set it to max_R
                    if R_temp >= self.max_R:
                        R_temp = self.max_R

                    # subtract the R_temp value from 4000 to find the offset of the biased values
                    R.append(4000-R_temp)
                self.resistance[i] = np.array(R)

                # add all 100 values together to find an average
                self.offset[i] = self.offset[i] + self.resistance[i]
        # find the average offset for each resistance value by dividing the sum by 100
        self.offset = [self.offset[i]/100.0 for i in range(0,11)]

        # assign the first resistance values to initialize the low-pass filter values
        self.filtered_output = self.resistance.flatten()


        while not rospy.is_shutdown():

            ######################################################################################
            #this could work generally for for multiple sections
            ######################################################################################
            # num_patches = 3
            # ADC_result = np.array([])
            # for j in xrange(num_patches):
            #     ADC_buf = []
            #     ADC_buf_arr = np.array([np.vstack((ADC_buf, self.ADC_list_of_dicts[i])) for i in xrange(11)])
            #     ADC_result = np.hstack((ADC_result, ADC_buf_arr))
            ######################################################################################                

            self.fc = 1.0
            self.a = (2*pi*np.diff(self.dt)*self.fc)/(2*pi*np.diff(self.dt)*self.fc+1)
            
            for i in range(0,11):
                R=[]
                F=[]
                for j in range(0,27):
                    if self.ADC_reading[i][j] < 1.0:
                        self.ADC_reading[i][j]=1.0
                    R_temp = round(-2200.0*(-5.0 + (5.0/256)*sum((self.ADC_reading[i])))/((5.0/256)*self.ADC_reading[i][j]),0)
                    if R_temp >= self.max_R:
                        R_temp = self.max_R
                    # F_temp = 500/(0.1*R_temp-30.0)-1.4 # good match for unloading curve 
                    # F_temp = 500/(0.35*R_temp-175.0)-.2 # good match for loading curve
                    F_temp = 500/(0.35*R_temp-400.0)-.2 # good match for loading curve
                    R.append(R_temp)
                    F.append(round(F_temp,2))
                self.resistance[i] = np.array(R)
                self.force_array[i]=np.array(F)
           
            self.resistance = [self.resistance[i]+self.offset[i] for i in range(0,11)]
        
            for i in range(0,11):
                for j in range(0,27):
                    self.square_array[i][j].color.b = self.resistance[i][j]/4000
                    self.square_array[i][j].color.r = 1 - self.resistance[i][j]/4000
                    self.pub.publish(self.square_array[i][j])

            self.filtered_output = self.a*np.array(self.resistance).flatten()+(1-self.a)*self.filtered_output
            
            # publish the forces and resistances as a flattened matrix
            self.pub_resistance.publish(np.array(self.resistance).flatten())
            self.pub_force.publish(self.force_array.flatten()-.3)
            self.pub_time.publish(round(rospy.get_time(),5)-self.t0)
            self.pub_filtered.publish(self.filtered_output)
            self.pub_ADC.publish(np.array(self.ADC_reading).flatten())
            self.dt.append(round(rospy.get_time(),5))
            self.rate.sleep()
                    
                
if __name__=='__main__':
    
    # initializa a ROS node for the markers
    rospy.init_node('square_markers',anonymous = True)
    visualize = grid_visualization()
    visualize.run()
