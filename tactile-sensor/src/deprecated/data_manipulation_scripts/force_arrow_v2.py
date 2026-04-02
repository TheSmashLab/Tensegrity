#!/usr/bin/env python

# Authror: Nathan Day
# Date: February 12, 2016
# Description:
#     This is a test script for rviz to publish a cylidrical marker along with arrows to display force being applied to a taxel

import rospy
from math import cos, sin, pi, atan2
import numpy as np
from visualization_msgs.msg import Marker
from serial_data.msg import calibration2
from visualization_msgs.msg import MarkerArray
import tf.transformations as tft

class tactile_visualization():
   
   def __init__(self):

      self.data_in = None

      # initialize a subscriber for incoming tactile data
      rospy.Subscriber('tactile_data', calibration2, self.callback, tcp_nodelay=False)
      
      while self.data_in == None:
         rospy.sleep(0.1)

      # initialize a publisher for the marker
      self.pub = rospy.Publisher('/cylinder', Marker, queue_size = 1) 
      self.rate = rospy.Rate(100)

      # initialize cylidrical marker      
      self.cyl = Marker()
      self.cyl.header.frame_id = self.data_in.header.frame_id
      self.cyl.ns = 'my_cylinder'
      self.cyl.type = Marker.CYLINDER
      self.cyl.action = 0
      # set the scale orientation and position of the marker
      self.cyl.scale.x = 17
      self.cyl.scale.y = 17
      self.cyl.scale.z = 22
      self.cyl.pose.position.x = 0.0
      self.cyl.pose.position.y = 0.0
      self.cyl.pose.position.z = 0.0

      quat = tft.quaternion_from_euler(0,0,0)

      self.cyl.pose.orientation.x = quat[0]
      self.cyl.pose.orientation.y = quat[1]
      self.cyl.pose.orientation.z = quat[2]
      self.cyl.pose.orientation.w = quat[3]
      
      # set the color of the marker
      self.cyl.color.r = 0.0
      self.cyl.color.g = 0.0
      self.cyl.color.b = 1.0
      self.cyl.color.a = 0.5
      
      # set the marker duration
      self.cyl.lifetime = rospy.rostime.Duration()
      
      # initialize array for arrow markers
      self.arrow_array = []
      self.theta = np.zeros(12)

      for i in range(0,12):

         # initialize theta for each arrow from the unit vector
         self.theta[i] =  atan2(self.data_in.direction[i].z,self.data_in.direction[i].y)
         
         # initialize ararrow marker
         self.arrow = Marker()
         self.arrow.header.frame_id = self.data_in.header.frame_id
         self.arrow.ns = 'my_arrow '+ str(i)
         self.arrow.type = Marker.ARROW
         self.arrow.action = 0
         self.arrow.frame_locked = True
         
         # set the scale orientation and position of the arrow marker
         self.arrow.scale.x = 10.0
         self.arrow.scale.y = 1.0
         self.arrow.scale.z = 1.0
         self.arrow.pose.position.x = -8.5*cos(self.theta[i]) #100.0*self.data_in.position[i].x
         self.arrow.pose.position.y = -8.5*sin(self.theta[i]) #100.0*self.data_in.position[i].y 
         self.arrow.pose.position.z = 10.0 + 100.0*self.data_in.position[i].x  #100.0*self.data_in.position[i].z
         
         
         quat_arrow = tft.quaternion_from_euler(0,0,self.theta[i])

         self.arrow.pose.orientation.x = quat_arrow[0]
         self.arrow.pose.orientation.y = quat_arrow[1]
         self.arrow.pose.orientation.z = quat_arrow[2]
         self.arrow.pose.orientation.w = quat_arrow[3]
         
         # set the color of the marker
         self.arrow.color.r = 0.0
         self.arrow.color.g = 1.
         self.arrow.color.b = 0.1
         self.arrow.color.a = 1.0
         
         # set the marker duration
         self.arrow.lifetime = rospy.rostime.Duration()
         
         self.arrow_array.append(self.arrow)

   # create a callback function to be run whenever the subscriber receives new data
   def callback(self, msg):
      self.data_in = msg
     
      
   def run(self):
      while not rospy.is_shutdown():
         self.pub.publish(self.cyl)
         for i in range(0,12):
            self.arrow_array[i].scale.x = 10.0 + 10.0*self.data_in.force[i]/6.0
            self.arrow_array[i].color.r = self.data_in.force[i]/12.0
            self.arrow_array[i].pose.position.y = -(8.5 + self.arrow_array[i].scale.x)*sin(self.theta[i])
            self.arrow_array[i].pose.position.x = -(8.5 + self.arrow_array[i].scale.x)*cos(self.theta[i])
            self.pub.publish(self.arrow_array[i])
         self.rate.sleep()

if __name__=='__main__':
   

   # initialize a ROS node for the markers
   rospy.init_node('markers', anonymous=True)

   visualize = tactile_visualization()

   visualize.run()

