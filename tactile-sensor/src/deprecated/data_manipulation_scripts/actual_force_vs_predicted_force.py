#!/usr/bin/env python

import rospy
import numpy as np
from visualization_msgs.msg import Marker
from std_msgs.msg import String
from tactile_sensor.msg import resistance as res
from math import sin, cos, pi
import tf.transformations as tft
from geometry_msgs.msg import WrenchStamped as wrench
from time import time, sleep, clock

class actual_vs_predicted():


    def __init__(self):

        self.force_in = None
        self.data_in = None
        self.force_calibrated_in = np.array(np.zeros(297))

         # initialize a subscriber for force torque sensor
        rospy.Subscriber('/ftnode1/netft_data', wrench, self.get_force, tcp_nodelay=True)

        # initialize a subscriber for resistance values
        rospy.Subscriber('/calibrated_forces', res, self.get_force_calibrated, tcp_nodelay=True)

        while self.force_calibrated_in == None:
            rospy.sleep(0.01)
            print('Look here!')

        while self.force_in == None:
            rospy.sleep(0.01)
            print('Look there!')

    def get_force(self, msg):
        self.force_in = msg.wrench.force.z

    def get_force_calibrated(self, msg):
        self.force_calibrated_in = msg.resistance

    def init_file(self):
        self.file = open('predicted_vs_actual_force.txt','w')

    def close_file(self):
        self.file.close()

    def run(self):

        while not rospy.is_shutdown():

            avg_predicted = sum(self.force_calibrated_in)


           # if self.cnt_f != 0:
            actual = self.force_in

           # if (self.cnt_f != 0) and (self.cnt != 0):
            print('Predicted = ' + str(avg_predicted) + '\t' + 'Actual = ' + str(-actual) + '\n')

            self.file.write(str(clock()) + '\t' + str(avg_predicted) + '\t' + str(-actual) + '\n')

            sleep(0.1)

if __name__ =='__main__':

    rospy.init_node('correlation_values',anonymous=True)

    obj = actual_vs_predicted()
    obj.init_file()
    rospy.on_shutdown(obj.close_file)
    obj.run()
