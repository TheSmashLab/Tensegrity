#!/usr/bin/env python

import rospy
import numpy as np
from serial_data.msg import resistance as res
from geometry_msgs.msg import WrenchStamped as wrench

class force_calibration():

    def __init__(self):

        self.file_name = None
        self.record = None
        self.file = None

        self.force_prev = 0

        self.force_in = 0

        zeros_27 = np.array([0 for i in range(0,27)])

        self.res_in = {0: zeros_27 ,1: zeros_27, 2: zeros_27, 3: zeros_27, 4: zeros_27, 5: zeros_27, 6: zeros_27, 7: zeros_27, 8: zeros_27, 9: zeros_27, 10: zeros_27}

        self.force_calibrated_in = {0: zeros_27 ,1: zeros_27, 2: zeros_27, 3: zeros_27, 4: zeros_27, 5: zeros_27, 6: zeros_27, 7: zeros_27, 8: zeros_27, 9: zeros_27, 10: zeros_27}

        # initialize a subscriber for force torque sensor
        rospy.Subscriber('/ftnode1/netft_data', wrench, self.get_force, tcp_nodelay=True)

        # initialize a subscriber for resistance values
        rospy.Subscriber('resistance_values', res, self.get_res, tcp_nodelay=True)

        # initialize a subscriber for resistance values
        rospy.Subscriber('force_values', res, self.get_force_calibrated, tcp_nodelay=True)

        
        
    def get_force(self, msg):
        self.force_in = msg.wrench.force.z


    def get_res(self, msg):
        resistance = msg.resistance
        self.res_in[resistance[0]] = resistance[1:28]


    def get_force_calibrated(self, msg):
        force = msg.resistance
        self.force_calibrated_in[force[0]] = force[1:28]


    def init_file_write(self):
        self.file_name = "force_calibrated_vs_actual_3-3.txt"
        self.file = open(self.file_name, 'w')
        

    def close_file(self):
        self.file.close()

        
    def run(self):
        while not rospy.is_shutdown():
            for i in range(0,11):
                for j in range(0,27):
                    taxel = self.res_in[i][j]
                    force = self.force_calibrated_in[i][j]
                    if(i==2 and j==2):
                        if self.force_prev != self.force_in:
                            print(str(taxel)+'\t'+str(-self.force_in)+'\t'+str(force)+'\n')                        
                            self.file.write(str(taxel))
                            self.file.write('\t')
                            self.file.write(str(self.force_in))
                            self.file.write('\t')
                            self.file.write(str(force))
                            self.file.write('\n')
                            self.force_prev = self.force_in


if __name__ =='__main__':

    rospy.init_node('correlation_values',anonymous=True)

    correlation = force_calibration()

    correlation.init_file_write()

    rospy.on_shutdown(correlation.close_file)

    correlation.run()
