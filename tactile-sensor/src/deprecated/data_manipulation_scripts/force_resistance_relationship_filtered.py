#!/usr/bin/env python

import rospy
import numpy as np
from serial_data.msg import resistance as res
from geometry_msgs.msg import WrenchStamped as wrench
from collections import deque as deq

class force_calibration():

    def __init__(self):

        self.file_name = None
        self.record = None
        self.file = None
        
        # deques for unfiltered incoming data
	self.taxel_deq = deq([1],maxlen=30)
        self.force_deq = deq([1],maxlen=30)

        # deques for the filtered data values
	self.taxel_ave_deq = deq([1],maxlen=30)
        self.force_ave_deq = deq([1],maxlen=30)

	self.average_taxel = 0
        self.average_force = 0

        self.sum_taxel = 0
        self.sum_force = 0

	self.force_prev = 0
	
        self.force_in = 0

        zeros_27 = np.array([0 for i in range(0,27)])

        self.res_in = {0: zeros_27 ,1: zeros_27, 2: zeros_27, 3: zeros_27, 4: zeros_27, 5: zeros_27, 6: zeros_27, 7: zeros_27, 8: zeros_27, 9: zeros_27, 10: zeros_27}

        # initialize a subscriber for force torque sensor
        rospy.Subscriber('/ftnode1/netft_data', wrench, self.get_force, tcp_nodelay=True)

        # initialize a subscriber for resistance values
        rospy.Subscriber('resistance_values', res, self.get_res, tcp_nodelay=True)
    
    def get_force(self, msg):
        self.force_in = round(msg.wrench.force.z,2)


    def get_res(self, msg):
        resistance = msg.resistance
        self.res_in[resistance[0]] = resistance[1:28]


    def init_file_write(self):
        file_load = "grid_calibration_loading_filtered_"
        file_unload = "grid_calibration_unloading_filtered_"
        file_unfiltered = "grid_calibration_unfiltered_"
        self.row = input("what row would you like to sample (0-10)? - ")
        file_load += str(self.row)
        file_unload += str(self.row)
        file_unfiltered += str(self.row)
        file_load += "-"
        file_unload += "-"
        file_unfiltered += "-"
        self.col = input("what column would you like to sample (0-26)? - ") 
        file_load += str(self.col)
        file_unload += str(self.col)
        file_unfiltered += str(self.row)
        file_load += ".txt"
        file_unload += ".txt"
        file_unfiltered += ".txt"
        self.file_name_load = file_load
        self.file_name_unload = file_unload
        self.file_name_unfiltered = file_unfiltered
        self.file_load = open(self.file_name_load, 'w')
        self.file_unload = open(self.file_name_unload, 'w')
        self.file_unfiltered = open(self.file_name_unfiltered, 'w')
        

    def close_file(self):
        self.file_load.close()
        self.file_unload.close()

        
    def run(self):
        while not rospy.is_shutdown():
            for i in range(0,11):
                for j in range(0,27):

                    # once the taxel of interest's location of the array is reached, write data to file
                    if(i==int(self.row) and j==int(self.col)):
                        
                        # to avoid duplicate data pairs, wait to append and write to file, until the previous reading differs from the current one
                        if self.force_prev != self.force_in:

                            # build deques for the unfiltered resistance data and the moving average resistance data
                            
                            self.file_unfiltered.write(str(self.res_in[i][j]))
                            self.file_unfiltered.write('\t')
                            self.file_unfiltered.write(str(self.force_in))
                            self.file_unfiltered.write('\n')

                            self.taxel_deq.append(self.res_in[i][j])
                            self.sum_taxel = sum(list(self.taxel_deq))
                            self.average_taxel = self.sum_taxel/float(len(list(self.taxel_deq)))
                            self.taxel_ave_deq.append(self.average_taxel)

                            # build deques for the unfiltered force data and the moving average force data
                            self.force_deq.append(self.force_in)
                            self.sum_force = sum(list(self.force_deq))
                            self.average_force = self.sum_force/float(len(list(self.force_deq)))
                            self.force_ave_deq.append(self.average_force)
                            
                           # Create dummy values to pair with average taxel deque values 
                           # This is necessary, because in order to determine loading and unloading the slopes have to change. When paired with the force values the slopes are almost always positive. When paired with values ranging from 50 to 1000 by steps of 50, the slopes can change between loading and unloading.

                            self.indices = [(i+1)*50 for i in range(0,len(self.taxel_ave_deq))]                            

                            print(str(self.average_taxel)+'\t'+str(self.average_force)+ '\t'+str(np.polyfit(self.taxel_ave_deq, self.indices, 1)[0])+'\n')      
                            
                            # if the slope of a line fit to the samples in the deq is negative write data to the loading file
                            if(np.polyfit(self.taxel_ave_deq, self.indices, 1)[0] < 0):
                                self.file_load.write(str(self.average_taxel))
                                self.file_load.write('\t')
                                self.file_load.write(str(self.average_force))
                                self.file_load.write('\t')                                
                                self.file_load.write(str(np.polyfit(self.taxel_deq, self.indices, 1)[0]))
                                self.file_load.write('\n')

                            if(np.polyfit(self.taxel_ave_deq, self.indices, 1)[0] > 0):
                                self.file_unload.write(str(self.average_taxel))
                                self.file_unload.write('\t')
                                self.file_unload.write(str(self.average_force))
                                self.file_unload.write('\t')                                
                                self.file_unload.write(str(np.polyfit(self.taxel_deq, self.indices, 1)[0]))
                                self.file_unload.write('\n')

                            self.force_prev = self.force_in


if __name__ =='__main__':

    rospy.init_node('correlation_values',anonymous=True)

    correlation = force_calibration()

    correlation.init_file_write()

    rospy.on_shutdown(correlation.close_file)

    correlation.run()
