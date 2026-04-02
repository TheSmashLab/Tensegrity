#! /usr/bin/env python3

import rospy
from std_msgs.msg import UInt16MultiArray, MultiArrayLayout, MultiArrayDimension
import time
import serial
import numpy as np
import sys
from threading import Thread

# np.set_printoptions(threshold=sys.maxsize)

class TactileSensorRepeater():
    
    def __init__(self, rate=20, sensor_size=(64,16), max_num_sensors=8):
        rospy.init_node('tactile_repeater', anonymous=True)
        self.rate = rate
        self.ros_rate = rospy.Rate(rate)
        self.pub_sensors = [None] * max_num_sensors
        self.arduino_serial = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
            )   #serial object, port must be correct
        self.sensor_size = sensor_size
        self.num_sensors = None
        self.enable_publishing = False
        self.namespace = rospy.get_namespace()

        self.data = None
        self.sensor_ids = None
        self.print_ids = True

        self.pub_message = UInt16MultiArray()
        self.pub_message.layout.dim = [MultiArrayDimension(), MultiArrayDimension()]
        self.pub_message.layout.dim[0].label = "rows"
        self.pub_message.layout.dim[0].size = self.sensor_size[0]
        self.pub_message.layout.dim[0].stride = self.sensor_size[1]*self.sensor_size[0]
        self.pub_message.layout.dim[1].label = "colums"
        self.pub_message.layout.dim[1].size = self.sensor_size[1]
        self.pub_message.layout.dim[1].stride = self.sensor_size[1]
        self.pub_message.layout.data_offset = 0
        self.pub_message.data = []

    def initialize_data_aquisition(self):
        self.sensor_thread = Thread(target=self.read_sensors)
        self.sensor_thread.start()

    def read_sensors(self):
        count = 0
        report_period = 10
        init_time = time.time()
        while not rospy.is_shutdown():
            while not rospy.is_shutdown():  #keep end byte as the end. this will ensure that the position doesn't drift
                stop_1 = self.arduino_serial.read(1)
                if(stop_1 == b'\xff'):
                    stop_2 = self.arduino_serial.read(1)
                    if(stop_2 == b'\xff'):
                        break

            new_num_sensors = np.array([self.arduino_serial.read(2)]).view(np.uint16).squeeze()
            if(self.num_sensors is None):
                self.num_sensors = new_num_sensors
                self.enable_publishing = True
            elif(not new_num_sensors == self.num_sensors):
                self.num_sensors = new_num_sensors
                self.print_ids = True

            if(self.num_sensors > 0):
                self.sensor_ids = np.array([self.arduino_serial.read(2*self.num_sensors)]).view(np.uint16).tolist()
                self.data = np.array([self.arduino_serial.read(2*self.num_sensors*self.sensor_size[1]*self.sensor_size[0])]).view(np.uint16).tolist()
                if(self.print_ids):
                    print("Publish ID's Updated: {}".format(self.sensor_ids))
                    self.print_ids = False
                # print(self.sensor_ids)
                # print(self.pub_message.data)
            else:
                self.data = None
                self.sensor_ids = []

            for i in range(len(self.pub_sensors)):
                if(i in self.sensor_ids and self.pub_sensors[i] is None):
                    self.pub_sensors[i] = rospy.Publisher(self.namespace + str(i), UInt16MultiArray, queue_size=1)
                elif(i not in self.sensor_ids and self.pub_sensors[i] is not None):
                    self.pub_sensors[i].unregister()
                    self.pub_sensors[i] = None
            count += 1
            curr_time = time.time()
            if(curr_time - init_time > report_period):
                rate = round(count/(curr_time - init_time),2)
                print("Sensor refresh rate: {}Hz".format(rate))
                count = 0
                init_time = curr_time

    
    def publish(self):
        while(not self.enable_publishing and not rospy.is_shutdown()):
            self.ros_rate.sleep()
        print("Publishing data for {} sensor(s) of size {}x{} at a rate of {}Hz".format(self.num_sensors,self.sensor_size[0],self.sensor_size[1],self.rate))
        while not rospy.is_shutdown():
            for i in range(len(self.sensor_ids)):
                self.pub_message.data = self.data[i*self.sensor_size[0]*self.sensor_size[1]:(i+1)*self.sensor_size[0]*self.sensor_size[1]]
                # print(self.sensor_ids[i])
                # print(self.pub_message.data)
                try:
                    self.pub_sensors[self.sensor_ids[i]].publish(self.pub_message)
                except AttributeError as e:
                    pass
            self.ros_rate.sleep()

if __name__ == '__main__':
    # try:
    repeater = TactileSensorRepeater()
    repeater.initialize_data_aquisition()
    repeater.publish()
    # except Exception as e:
    #     print("Failed to run: {}".format(str(e)))