#!/usr/bin/env python

# Authror: Nathan Day
# Date: February 12, 2016
# Description:
#     This is a test script for rviz to publish a rectangular marker along with arrows to display force being applied to a taxel

import rospy
import numpy as np
from visualization_msgs.msg import Marker
from serial_data.msg import calibration
from visualization_msgs.msg import MarkerArray
import tf.transformations as tft

class tactile_visualization():
   
   def __init__(self):

    
      # initialize a subscriber for incoming tactile data
      rospy.Subscriber('tactile_data', calibration, self.callback, tcp_nodelay=False)
    
      # initialize a publisher for the marker
      self.pub = rospy.Publisher('/rectangle', Marker, queue_size = 1) 
      # self.pub2 = rospy.Publisher('/arrow', Marker, queue_size = 1)
      self.rate = rospy.Rate(100)

      # create variable for the incoming force
      self.force_incoming = 0

      # initialize the arrow_array variable
      self.arrow_array = []

      # initialize rectangular marker      
      self.rect = Marker()
      self.rect.header.frame_id = '/my_frame'
      self.rect.ns = 'my_rectangle'
      self.rect.type = Marker.CUBE
      self.rect.action = 0
      
      # set the scale orientation and position of the marker
      self.rect.scale.x = 6
      self.rect.scale.y = 2
      self.rect.scale.z = 0.1
      self.rect.pose.position.x = 0.0
      self.rect.pose.position.y = 0.0
      self.rect.pose.position.z = 0.0
      self.rect.pose.orientation.x = 0.0
      self.rect.pose.orientation.y = 0.0
      self.rect.pose.orientation.z = 0.0
      self.rect.pose.orientation.w = 1.0
      # set the color of the marker
      self.rect.color.r = 0.4
      self.rect.color.g = 0.5
      self.rect.color.b = 0.1
      self.rect.color.a = 1.0
      
      # set the marker duration
      self.rect.lifetime = rospy.rostime.Duration()
      
      # initialize all the arrows for all 12 taxels
      for i in range(0,12):          

          # initialize ararrow marker
          self.arrow = Marker()
          self.arrow.header.frame_id = '/my_frame'
          self.arrow.ns = 'my_arrow ' + str(i) 
          self.arrow.type = Marker.ARROW
          self.arrow.action = 0
          
          # solve the quaternion for rotation about the x axis
          self.quat = tft.quaternion_from_euler(0,3.14159/2,0)
          print(self.quat)
          
          # set the scale orientation and position of the arrow marker
          self.arrow.scale.x = 1.0
          self.arrow.scale.y = .1
          self.arrow.scale.z = .1
          if i < 3:
              self.arrow.pose.position.x = 0.5 + i
              self.arrow.pose.position.y = 0.5
          if ((i >= 3) and (i < 6)):
              self.arrow.pose.position.x = 5.5 - i 
              self.arrow.pose.position.y = -0.5
          if ((i >= 6) and (i < 9)):
              self.arrow.pose.position.x = -(i - 5.5)
              self.arrow.pose.position.y = -0.5
          if ((i >= 9) and (i < 12)):
              self.arrow.pose.position.x = -(11.5 - i)
              self.arrow.pose.position.y = 0.5
          self.arrow.pose.position.z = 1.05
          self.arrow.pose.orientation.x = self.quat[0]
          self.arrow.pose.orientation.y = self.quat[1]
          self.arrow.pose.orientation.z = self.quat[2]
          self.arrow.pose.orientation.w = self.quat[3]
          
          # set the color of the marker
          self.arrow.color.r = 0.0
          self.arrow.color.g = 0.5
          self.arrow.color.b = 0.5
          self.arrow.color.a = 1.0
      
          # set the marker duration
          self.arrow.lifetime = rospy.rostime.Duration()
          
          # assign each arrow marker to the arrow_array
          self.arrow_array.append(self.arrow)

   # create a callback function to be run whenever the subscriber receives new data
   def callback(self, calibration):
      self.force_incoming = calibration.force
      self.arrow.scale.x = 1.0 + self.force_incoming[0]/6.0
      self.arrow.pose.position.z = 1.05 + self.force_incoming[0]/6.0
      # print self.force_incoming[0]
      for i in range(0,12):
          self.arrow_array[i].scale.x =  1.0 + self.force_incoming[i]/6.0
          self.arrow_array[i].pose.position.z =  1.05 + self.force_incoming[i]/6.0
      
if __name__=='__main__':
   
   # initialize a ROS node for the markers
   rospy.init_node('markers', anonymous=True)

   visualize = tactile_visualization()
   
   while not rospy.is_shutdown():
      visualize.pub.publish(visualize.rect)
      for i in range(0,12):
          visualize.pub.publish(visualize.arrow_array[i])
      visualize.rate.sleep()
