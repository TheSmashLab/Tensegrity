#!/usr/bin/env python

import numpy as np
import pdb
import matplotlib.pyplot as plt
import sys
from collections import deque as deq
from scipy.optimize import curve_fit

class plot_test_data():
    
    def __init__(self):

        self.a = 0
        # self.size = len(self.data)

    # def print_data(self):

    #     print self.data
    #     print len(self.data)


    # def sort(self):
    #     #pdb.set_trace()
    #     self.data.sort(axis=0)
                    

    def init_file_write(self):
        
        self.file_name = "sorted_data.txt"
        self.file = open(self.file_name, 'w')

    def write_file(self):
        
        for i in range(0,len(self.data)):
            self.file.write(str(self.data[i]))
            self.file.write('\n')


    def plot_data(self, x, y, y_fit, color_line, color_fit):
        plt.plot(x, y, color_line)
        plt.plot(x, y_fit, color_fit)


    def line_fit(self, x, y):
        def func(x, a, b):
            return a*1/(x-b)
        popt, pcov = curve_fit(func, x, y)
        y_fit_data = popt[0]*1/(x - popt[1]) 
        return y_fit_data

if __name__=='__main__':

    data_a = np.genfromtxt('/home/nmd89/git/byu/development/tactile_sensor/tactile_catkin_ws/src/serial_data/scripts/grid_calibration_loading_filtered_10-23.txt', dtype=None, delimiter='\t')

    data_b = np.genfromtxt('/home/nmd89/git/byu/development/tactile_sensor/tactile_catkin_ws/src/serial_data/scripts/grid_calibration_unloading_filtered_10-23.txt', dtype=None, delimiter='\t') # np.genfromtxt('/home/nmd89/grid_calibration_loading_filtered_5-5.txt', dtype=None, delimiter='\t')

    data_c = np.genfromtxt('/home/nmd89/git/byu/development/tactile_sensor/tactile_catkin_ws/src/serial_data/scripts/grid_calibration_unfiltered_10-10.txt', dtype=None, delimiter='\t')#np.genfromtxt('/home/nmd89/grid_calibration_unloading_filtered_5-5.txt', dtype=None, delimiter='\t')

    a = plot_test_data()
    b = plot_test_data()
    c = plot_test_data()

    a_fit = a.line_fit(data_a[:,0], data_a[:,1])
    b_fit = b.line_fit(data_b[:,0], data_b[:,1])
    c_fit = c.line_fit(data_c[:,0], data_c[:,1])
    
    plt.figure(1)
    plt.subplot(221)
    a.plot_data(data_a[:,0], data_a[:,1], a_fit, 'b.', 'yo')
    plt.title('unfiltered_data')

    plt.subplot(222)
    b.plot_data(data_b[:,0], data_b[:,1], b_fit, 'b.', 'ro')
    plt.title('filtered_loading')

    plt.subplot(223)
    c.plot_data(data_c[:,0], data_c[:,1], c_fit, 'b.', 'ro')
    plt.title('filtered_unloading')

    plt.subplot(224)
    a.plot_data(data_a[:,0], data_a[:,1], a_fit, 'b.', 'yo')
    b.plot_data(data_b[:,0], data_b[:,1], b_fit, 'b.', 'go')
    c.plot_data(data_c[:,0], data_c[:,1], c_fit, 'b.', 'ro')
    plt.title('filtered_unfiltered_overlay')

    plt.show()

    # collect_data.print_data()

    # collect_data.sort()

    # collect_data.print_data()

    # collect_data.init_file_write()
    
    # collect_data.write_file()


