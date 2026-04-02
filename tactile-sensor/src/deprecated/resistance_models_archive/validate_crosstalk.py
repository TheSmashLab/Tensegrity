#!/usr/bin/env python

import rospy
import numpy as np
from std_msgs.msg import String
from std_msgs.msg import Float64
from tactile_sensor.msg import resistance as res
from geometry_msgs.msg import WrenchStamped
from collections import deque as deq
from scipy.io import savemat
import matplotlib.pyplot as plt
import copy
import pdb

class space_effect():

    def __init__(self):

        self.m = 3 #int(raw_input('Insert # of Rows: '))
        self.n = 3 #int(raw_input('Insert # of Cols: '))
        self.mat = {'volts':deq([]), 'force':deq([])}

        self.data_in = None
        self.resistor_0 = None
        
        self.ADC_reading = np.array(np.zeros([self.m,self.n]))

        #initialize two subscribers for incoming serial data
        rospy.Subscriber('serial',String,self.callback,tcp_nodelay=False)

        # initialize a subscriber for force torque sensor
        rospy.Subscriber('/netft_data', WrenchStamped, self.get_force, tcp_nodelay=True)

        # while self.data_in == None:
        #     rospy.sleep(0.01)
        #     print 'loading ADC...'

        rospy.Subscriber('resistance_values_new', res, self.get_resistance, tcp_nodelay=False)

        while self.resistor_0 == None:
            rospy.sleep(0.01)
            print('loading resistance...')

        while self.force_in == None:
            rospy.sleep(0.01)
            print('loading force...')
       
    def callback(self,msg):
        self.data_in = msg.data
        data = np.fromstring(self.data_in, count = (self.n+1), sep = ',')
        self.ADC_reading[int(data[0])] = data[1:(self.n+1)]

    def write_file(self):
        print('writing to file...')
        savemat('validation_diode', self.mat)

    def get_force(self, msg):
        self.force_in = msg.wrench.force.z


    # callback for resistance
    def get_resistance(self, msg):
        self.resistor_0 = msg.resistance[0]


    def run(self):
        
        input('press Enter when ready to record')
        while not rospy.is_shutdown():
            self.mat['volts'].append(self.ADC_reading[0][0])
            # self.mat['volts'].append(self.resistor_0)
            self.mat['force'].append(self.force_in)
            rospy.sleep(0.01)
        

if __name__=='__main__':

    # initializa a ROS node for the markers
    rospy.init_node('space',anonymous = True)
    visualize = space_effect()
    rospy.on_shutdown(visualize.write_file)
    visualize.run()
