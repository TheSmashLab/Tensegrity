#! /usr/bin/env python3

import rospy
from std_msgs.msg import UInt16MultiArray, MultiArrayLayout, MultiArrayDimension
import time
import serial
import numpy as np
import yaml
import sys
from scipy.optimize import curve_fit
# from scipy.linalg import null_space
import matplotlib.pyplot as plt

np.set_printoptions(threshold=sys.maxsize)

class TactileSensorCalibrator():
    
    def __init__(self, sleeve_name, sensor_space="main", sensor_id=0, lpf_alpha=0.9):
        rospy.init_node('tactile_plotter', anonymous=True)
        self.sleeve_name = sleeve_name
        self.plots_initialized = False
        self.sensor_space = sensor_space
        self.sensor_id = sensor_id
        self.lpf_alpha = lpf_alpha
        self.force_data_points = None
        self.first_reading = True
        self.sub_sensor = rospy.Subscriber("/tactile/" + sensor_space + "/" + str(sensor_id), UInt16MultiArray, self.sensor_callback, queue_size=1)

    def get_resistance(self, raw_data, v_0=3.3, r_0=3000, adc_bits=12, num_columns=64, num_rows=16, a=-0.00005, b=5):
        init_time = time.time()
        v_data = v_0*raw_data.astype(np.float32)/(2**adc_bits)
        # print(np.amax(np.amax(v_data)))
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
            res_data[i,:] = np.array(1/r_k).reshape(16)   #res_data[i,:] = np.array(1/r_k).reshape(16)
        # print(np.amin(np.amin(res_data)))
        # print(np.mean(np.mean(res_data)))
        # print(res_data)
        return res_data/1000.0

    def store_intercept_data(self, wait_time=120):
        input("Press enter to save no-load data")
        self.intercept_data = self.res_data
        for i in range(wait_time * 100):
            self.intercept_data = np.minimum(self.intercept_data, self.res_data)
            # print("Current sum: {}".format(np.sum(np.sum(self.intercept_data))))
            time.sleep(0.01)
        self.intercept_data[self.intercept_data > np.median(self.intercept_data.reshape(1024))] = np.median(self.intercept_data.reshape(1024))
        # print(np.median(self.intercept_data.reshape(1024)))
        print("No-load data saved")

    # def store_intercept_data(self):
    #     file_name = "calibration_" + self.sleeve_name + ".yaml"
    #     with open(file_name, 'r') as file:
    #         data = yaml.safe_load(file)
    #     self.intercept_data = np.array(data['intercept']).reshape(64,16)
    #     print("No-load data saved")

    def store_fit_data(self, fit_order=1):
        self.force_data_matrix = np.zeros((fit_order+1, fit_order+1))
        self.force_applied_vector = np.zeros(fit_order+1).T
        self.resistance_points = np.array([])
        if(fit_order < 1):
            fit_order = 1
        for i in range(fit_order + 1):
            self.force_applied_vector[i] = float(input("Apply a force to the sleeve. What force is being applied?"))
            force_applied_data = self.res_data[self.res_data < self.intercept_data]
            self.resistance_points = np.append(self.resistance_points, force_applied_data)
            for j in range(fit_order + 1):
                self.force_data_matrix[i][j] = np.sum(np.power(force_applied_data,j))
        converged = False
        while not converged:
            best_fit = self.get_best_fit(self.force_applied_vector, self.force_data_matrix)
            self.print_fit_error(best_fit, self.force_applied_vector, self.resistance_points)
            self.plot_fit(best_fit, self.resistance_points)
            decision = input("Do you want to add more force readings? Y/N: ")
            if decision == "Y" or decision == "y" or decision == "yes":
                num_readings = int(input("How many more readings do you want to input?"))
                for i in range(num_readings):
                    self.force_applied_vector = np.append(self.force_applied_vector, np.array([float(input("Apply a force to the sleeve. What force is being applied?"))]))
                    # print(np.shape(self.force_applied_vector))
                    force_applied_data = self.res_data[self.res_data < self.intercept_data]
                    self.resistance_points = np.append(self.resistance_points, force_applied_data)
                    self.force_data_matrix = np.append(self.force_data_matrix, np.zeros((1,fit_order+1)), axis=0)
                    # print(np.shape(self.force_data_matrix))
                    for j in range(fit_order + 1):
                        self.force_data_matrix[-1][j] = np.sum(np.power(force_applied_data,j))
            else:
                converged = True
        self.best_fit = self.get_best_fit(self.force_applied_vector, self.force_data_matrix).tolist()
        decision = input("Do you want to set a maximum resistance for registering a force? Y/N: ")
        if decision == "Y" or decision == "y" or decision == "yes":
            self.max_force_res = float(input("What would you like to be the maximum resistance for registering a force?"))
        else:
            self.max_force_res = float(np.amax(self.intercept_data.reshape(1024)))
        print("Force data colection complete")

    def get_best_fit(self, force_applied_vector, force_data_matrix):
        print(force_applied_vector)
        print(force_data_matrix)
        force_data_inv = np.linalg.pinv(force_data_matrix)
        print(force_data_inv)
        best_fit = force_data_inv @ force_applied_vector
        print(best_fit)
        return best_fit

    def print_fit_error(self, fit, force_applied_vector, resistance_points):
        estimated_forces = np.zeros(np.shape(resistance_points))
        for i in range(np.size(fit)):
            estimated_forces = estimated_forces + fit[i] * np.power(resistance_points,i)
        print(estimated_forces)
        total_estimated_force = np.sum(estimated_forces)
        print(total_estimated_force)
        total_real_force = np.sum(force_applied_vector)
        print(total_real_force)
        percent_error = abs(total_real_force - total_estimated_force)/total_real_force * 100
        print("Fit Error: {}%".format(percent_error))

    def plot_fit(self, fit_coefficients, resistance_points):
        print(resistance_points)
        xseq = np.linspace(0, 100, num=1000)
        yseq = np.zeros(np.shape(xseq))
        resistance_points_forces = np.zeros(np.shape(resistance_points))
        for i in range(np.size(fit_coefficients)):
            yseq = yseq + fit_coefficients[i] * np.power(xseq, i)
            resistance_points_forces = resistance_points_forces + fit_coefficients[i] * np.power(resistance_points, i)

        plt.plot(xseq, yseq)
        plt.scatter(resistance_points, resistance_points_forces)
        print("View the graph and then close it")
        plt.show()
    
    def save_to_file(self):
        file_name = "calibration_" + sleeve_name + ".yaml"
        data = {'fit': self.best_fit, 'max_force_res': self.max_force_res, 'intercept': self.intercept_data.reshape(1024).tolist()}
        with open(file_name, 'w') as file:
            yaml.dump(data, file)
        print("Calibration data saved to file")
        
    def sensor_callback(self, msg:UInt16MultiArray):
        raw_data = np.array(msg.data[0:1024]).reshape(64,16).astype(np.uint16)
        # if self.first_reading:
        self.res_data = self.get_resistance(raw_data)
        #     self.first_reading = False
        # else:
        #     self.res_data = self.res_data * self.lpf_alpha + self.get_resistance(raw_data) * (1 - self.lpf_alpha)

               

if __name__ == '__main__':
    # try:
    sensor_space = "main"
    sensor_id = 0
    if(len(sys.argv) > 4):
        sensor_space = sys.argv[1]
        sensor_id = int(sys.argv[2])
        sleeve_name = sys.argv[3]
        fit_order = int(sys.argv[4])
    calibrator = TactileSensorCalibrator(sleeve_name, sensor_space, sensor_id)
    calibrator.store_intercept_data()
    calibrator.store_fit_data(fit_order=fit_order)
    calibrator.save_to_file()