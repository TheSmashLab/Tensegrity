#!/usr/bin/env python

import rospy
import numpy as np
from tactile_sensor.msg import resistance as res
from geometry_msgs.msg import WrenchStamped as wrench
from copy import copy
from pdb import set_trace as brake

class Calibration():

    def __init__(self):

        self.resistance_in = None
        self.force_in = None

         # initialize a subscriber for force torque sensor
        rospy.Subscriber('/ftnode1/netft_data', wrench, self.get_force, tcp_nodelay=True)

        # initialize a subscriber for resistance values
        rospy.Subscriber('/resistance_values_new', res, self.get_resistance, tcp_nodelay=True)

        while self.force_in == None:
            rospy.sleep(0.01)
            print('Look here!')

        while self.resistance_in == None:
            rospy.sleep(0.01)
            print('Look there!')

    def get_force(self, msg):
        self.force_in = msg.wrench.force.z

    def get_resistance(self, msg):
        self.resistance_in = msg.resistance

    def init_file(self):
        self.file = open('distributed_force_vs_average_resistance_partial_load_unload.txt', 'w')
        self.file2 = open('distributed_force_vs_median_resistance_partial_load_unload.txt', 'w')

    def close_file(self):
        self.file.close()
        self.file2.close()

    def run(self):

        while not rospy.is_shutdown():
            force = copy(self.force_in)
            resistance = np.asarray(copy(self.resistance_in))

            # find the average and the median of all resistances < 4000.0
            resistance_ave = np.average(resistance[resistance < 3900.0])
            resistance_med = np.median(resistance[resistance < 3900.0])

            # brake()

            # add up the total number of active nodes (i.e. if resistance < 4000.0)
            active_nodes = float(len(resistance[resistance < 3900.0]))

            #  divide the force by the number of active nodes
            if active_nodes != 0:
                force_distributed = force/active_nodes

            print(str(resistance_ave) + ', ' + str(force_distributed) + '\t' + str(resistance_med) + ', ' + str(force_distributed))

            self.file.write(str(resistance_ave) + ', ' + str(force_distributed) + '\n')
            self.file2.write(str(resistance_med) + ', ' + str(force_distributed) + '\n')

            rospy.sleep(0.1)

if __name__ =='__main__':

    rospy.init_node('correlation_values',anonymous=True)

    obj = Calibration()
    obj.init_file()
    rospy.on_shutdown(obj.close_file)
    obj.run()
