#!/usr/bin/env python

from std_msgs.msg import String
from std_msgs.msg import Float64
from serial_data.msg import resistance as res
import rospy
import numpy as np

class class_name():

    def __init__(self):

        self.rate = rospy.Rate(80)

        self.resistor_1 = 0
        
        # subscribe to time
        rospy.Subscriber('time', Float64, self.get_time, tcp_nodelay=False)

        # subscribe to resistance
        rospy.Subscriber('resistance_values', res, self.get_resistance, tcp_nodelay=False)

        while self.resistor_1 == 0:
            self.rate.sleep()
        
    # callback for time
    def get_resistance(self, msg):
        self.resistor_1 = msg.resistance[1]
            
    def get_time(self, msg):
        self.time = msg.data
            
    def run(self):

        print('time','\t','resistance')
    
        while not rospy.is_shutdown():

            print(str(self.time), '\t', str(self.resistor_1))
            
            self.rate.sleep()
        

if __name__=='__main__':

    rospy.init_node('time_and_resistance', anonymous=True)

    obj = class_name()

    obj.run()
    
   
