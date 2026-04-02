#!/usr/bin/env python

# the purpose of this script is to visualize the force on the new tactile sensor on a grid of squares

import rospy
import numpy as np
from visualization_msgs.msg import Marker
from std_msgs.msg import String

class grid_visualization():

    def __init__(self):
        
        self.data_in = None
        self.square_array = [[],[],[],[],[],[]]
        self.data_matrix = []
        self.ADC_reading = {0: [0,0,0,0,0,0,0,0,0,0,0,0,0,0],1: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 2: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 3: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 4: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 5: [0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
        self.resistance = {0: [0,0,0,0,0,0,0,0,0,0,0,0,0,0],1: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 2: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 3: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 4: [0,0,0,0,0,0,0,0,0,0,0,0,0,0], 5: [0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
        #initialize a subscriber for incoming serial data
        rospy.Subscriber('serial',String,self.callback,tcp_nodelay=False)
        
        while self.data_in == None:
            rospy.sleep(0.01)

        # initialize a publisher for the markers
        self.pub = rospy.Publisher('/grid_squares', Marker, queue_size = 1)
        self.rate = rospy.Rate(100)
        
        # initialize the square markers
        for i in range(0,6):

            for j in range(0,14):

                
                self.square = Marker()
                self.square.header.frame_id = 'my_square'
                self.square.ns = 'square # ' + str(i) + ', ' + str(j)
                self.square.type = Marker.CUBE
                self.square.action = 0
                self.square.frame_locked = True
                self.square.scale.x = 1.25
                self.square.scale.y = 1.25
                self.square.scale.z = 0.125
                self.square.pose.position.x = i*1.25
                self.square.pose.position.y = j*1.25
                self.square.pose.position.z = 0
                self.square.color.r = 0.0
                self.square.color.g = 0.0
                self.square.color.b = 1.0
                self.square.color.a = 1.0
                self.square.lifetime = rospy.rostime.Duration()
                
                self.square_array[i].append(self.square)

    def callback(self,msg):
        self.data_in = msg.data
        data = np.fromstring(self.data_in, count = 15, sep = '\t')
        self.ADC_reading[data[0]] = data[1:15]

    def run(self):
        while not rospy.is_shutdown():
            
            for i in range(0,6):
                for j in range(0,14):
                    if self.ADC_reading[i][j]!=0:
                        R = round(-1200.0*(-5.0 + (5.0*sum(self.ADC_reading[i])/1024.0))/(5.0*self.ADC_reading[i][j]/1024.0),0)
                        if R >= 4000:
                            R = 4000
                        self.resistance[i][j] = R
                print(i)
                print(self.resistance[i])
                print("\n")

            for i in range(0,6):
                for j in range(0,14):
                    self.square_array[i][j].color.b = self.resistance[i][j]/4000
                    self.square_array[i][j].color.r = 1 - self.resistance[i][j]/4000
                    self.pub.publish(self.square_array[i][j-1])

            self.rate.sleep()
                    
                
if __name__=='__main__':
    
    # initializa a ROS node for the markers
    rospy.init_node('square_markers',anonymous = True)
    
    visualize = grid_visualization()

    visualize.run()
