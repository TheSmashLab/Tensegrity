#! /usr/bin/env python3

import rospy
from std_msgs.msg import UInt16MultiArray, MultiArrayLayout, MultiArrayDimension
import time
import serial
import numpy as np
import matplotlib.pyplot as plt
import sys
import yaml

np.set_printoptions(threshold=sys.maxsize)

class TactileSensorPlotter():
    
    def __init__(self, sleeve_name, sensor_space="main", sensor_id=0):
        rospy.init_node('tactile_plotter', anonymous=True)
        self.plots_initialized = False
        file_name = "calibration/calibration_" + sleeve_name + ".yaml"
        with open(file_name, 'r') as file:
            data = yaml.safe_load(file)
        self.intercept_data = np.array(data['intercept']).reshape(64,16)
        # print(self.intercept_data)
        self.fit = data['fit']
        self.max_force_res = data['max_force_res']
        self.last_res_data = np.zeros((64,16))
        self.sensor_space = sensor_space
        self.sensor_id = sensor_id
        self.sub_sensor = rospy.Subscriber("/tactile/" + sensor_space + "/" + str(sensor_id), UInt16MultiArray, self.sensor_callback, queue_size=1)
        print("Listening for tactile data...")
        rospy.spin()

    def get_resistance(self, raw_data, v_0=3.3, r_0=2000, adc_bits=12, num_columns=64, num_rows=16, a=-0.00005, b=5):
        init_time = time.time()
        v_data = v_0*raw_data.astype(np.float32)/(2**adc_bits)
        # print(v_data)
        res_data = np.zeros((num_columns, num_rows), dtype=np.float32)
        for i in range(num_columns):
            v_delta = np.repeat([-1 * v_data[i,:]], num_rows, axis=0).T.astype(np.float32)
            for j in range(num_rows):
                v_delta[j,j] = v_delta[j,j] + v_0
            # print(v_delta)
            v_delta_inv = np.linalg.inv(v_delta)
            # print(v_delta_inv)
            i_c = np.array([v_data[i,:]/r_0]).T
            # print(i_c)
            r_k = v_delta_inv @ i_c
            r_k[r_k == 0] = 1e-10
            # print(r_k)
            res_data[i,:] = np.array(1/r_k).reshape(16)
        # print(res_data[0,0])
        # force_data = res_data * a + b
        # force_data[force_data < 0] = 0
        # print(force_data)
        # print(time.time() - init_time)
        # print(np.amin(np.amin(res_data)))
        return res_data/1000.0

        
    def sensor_callback(self, msg:UInt16MultiArray):
        if(not self.plots_initialized):
            plt.ion()   #inisialize display
            self.fig1, self.ax1 = plt.subplots()
            array = np.random.randint(0, 63, size=(64,16), dtype=np.uint8)
            self.norm = plt.Normalize(0, 255)    #normalize on 0 to 250, decreasing upper limit will make forces stand our more
            self.axim1 = self.ax1.imshow(array, cmap="hot", norm=self.norm)
            self.plots_initialized = True

        raw_data = np.array(msg.data[0:1024]).reshape(64,16).astype(np.uint16)
        res_data = self.get_resistance(raw_data)
        # print(res_data)
        force_data = np.zeros(np.shape(res_data))
        # print(self.fit)
        for i in range(np.size(self.fit)):
            force_data[res_data < self.max_force_res] = force_data[res_data < self.max_force_res] + self.fit[i] * np.power(res_data[res_data < self.max_force_res],i)
        # force_data = np.maximum(force_data, np.zeros(np.shape(res_data)))
        # print(force_data)
        total_force = round(np.sum(np.sum(force_data)),2)
        if(total_force > 0):
            print("Force: {}".format(total_force))
        display_data = np.zeros(np.shape(res_data)).astype(np.uint16)
        display_data[res_data < self.intercept_data] = 50
        display_data = display_data + (force_data * 20).astype(np.uint16)
        display_data[display_data > 255] = 255
        display_data = display_data.astype(np.uint8)
        # display_data[self.last_res_data >= self.intercept_data] = 0
        self.last_res_data = res_data
        self.axim1.set_data(display_data) #set data to display
        self.fig1.canvas.flush_events()   #update display        

if __name__ == '__main__':
    # try:
    sensor_space = "main"
    sensor_id = 0
    if(len(sys.argv) > 3):
        sensor_space = sys.argv[1]
        sensor_id = int(sys.argv[2])
        sleeve_name = sys.argv[3]
    plotter = TactileSensorPlotter(sleeve_name, sensor_space, sensor_id)
    # except Exception as e:
    #     print("Failed to run: {}".format(str(e)))