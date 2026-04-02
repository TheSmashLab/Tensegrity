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


####  This is the marker for the stationary sphere for the elbow  ####

      # initialize the spherical marker
      self.sph = Marker()
      self.sph.header.frame_id = self.data_in.header.frame_id
      self.sph.ns = 'my_sphere'
      self.sph.type = Marker.SPHERE
      self.sph.action = 0

      # set the scale, orientation, and postion of the marker
      self.sph.scale.x = 20
      self.sph.scale.y = 20
      self.sph.scale.z = 20
      
      self.sph.pose.position.x = 0
      self.sph.pose.position.y = 0
      self.sph.pose.position.z = 0

      self.sph.color.r = 0.0
      self.sph.color.g = 0.0
      self.sph.color.b = 0.5
      self.sph.color.a = 1.0

      self.sph.lifetime = rospy.rostime.Duration()


####  This is the rotating cylinder marker ####

      # initialize cylidrical marker      
      self.cyl = Marker()
      self.cyl.header.frame_id = self.data_in.header.frame_id
      self.cyl.ns = 'my_cylinder'
      self.cyl.type = Marker.CYLINDER
      self.cyl.action = 0

      # set the scale orientation and position of the marker
      self.cyl.scale.x = 17
      self.cyl.scale.y = 17
      self.cyl.scale.z = 22 + 8
      self.cyl.pose.position.x = 0.0
      self.cyl.pose.position.y = 0.0
      self.cyl.pose.position.z = 11.0

      quat = tft.quaternion_from_euler(0,0,0)

      self.cyl.pose.orientation.x = quat[0]
      self.cyl.pose.orientation.y = quat[1]
      self.cyl.pose.orientation.z = quat[2]
      self.cyl.pose.orientation.w = quat[3]
      
      # set the color of the marker
      self.cyl.color.r = 0.0
      self.cyl.color.g = 0.0
      self.cyl.color.b = 0.5
      self.cyl.color.a = 1.0
      
      # set the marker duration
      self.cyl.lifetime = rospy.rostime.Duration()

####  This is the stationary cylinder marker ####

          # initialize cylidrical marker      
      self.cyl_2 = Marker()
      self.cyl_2.header.frame_id = self.data_in.header.frame_id
      self.cyl_2.ns = 'my_cylinder_2'
      self.cyl_2.type = Marker.CYLINDER
      self.cyl_2.action = 0

      # set the scale orientation and position of the marker
      self.cyl_2.scale.x = 17
      self.cyl_2.scale.y = 17
      self.cyl_2.scale.z = 22 + 8
      self.cyl_2.pose.position.x = 20.0 -4
      self.cyl_2.pose.position.y = 0.0
      self.cyl_2.pose.position.z = 0.0

      quat_2 = tft.quaternion_from_euler(0,pi/2,0)

      self.cyl_2.pose.orientation.x = quat_2[0]
      self.cyl_2.pose.orientation.y = quat_2[1]
      self.cyl_2.pose.orientation.z = quat_2[2]
      self.cyl_2.pose.orientation.w = quat_2[3]
      
      # set the color of the marker
      self.cyl_2.color.r = 0.0
      self.cyl_2.color.g = 0.0
      self.cyl_2.color.b = 0.5
      self.cyl_2.color.a = 1.0
      
      # set the marker duration
      self.cyl_2.lifetime = rospy.rostime.Duration()

      # set up a homogeneous matrix to be used for rotation about the y axis
      self.R_y = np.matrix([[cos(pi/2),0,-sin(pi/2),0],[0,1,0,0],[sin(pi/2),0,cos(pi/2),0],[0,0,0,1]])

      # rotate the cylinder about the y-axis
      cyl_pos = np.matrix([[self.cyl.pose.position.x],[self.cyl.pose.position.y],[self.cyl.pose.position.z],[1]])
      
      cyl_pos_new = self.R_y*cyl_pos
      
      self.cyl.pose.position.x = cyl_pos_new[0]
      self.cyl.pose.position.y = cyl_pos_new[1]
      self.cyl.pose.position.z = cyl_pos_new[2]

      quat_3 = tft.quaternion_from_matrix(self.R_y)

      self.cyl.pose.orientation.x = quat_3[0]
      self.cyl.pose.orientation.y = quat_3[1]
      self.cyl.pose.orientation.z = quat_3[2]
      self.cyl.pose.orientation.w = quat_3[3]

      
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
         self.arrow.scale.x = 0
         self.arrow.scale.y = 1.0
         self.arrow.scale.z = 1.0
         self.arrow.pose.position.x = 100*self.data_in.position[i].x#-8.5*cos(self.theta[i]) 
         self.arrow.pose.position.y = -100*self.data_in.position[i].y#-8.5*sin(self.theta[i]) 
         self.arrow.pose.position.z = -100*self.data_in.position[i].z#10.0 + 100.0*self.data_in.position[i].x  + 11.0
         
         # define a homogenous matrix for rotation about z for each arrow (no translation-this will be used for orientation only)
         self.R_x = np.matrix([[1,0,0,0],[0,cos(self.theta[i]),sin(self.theta[i]),0],[0,-sin(self.theta[i]),cos(self.theta[i]),0],[0,0,0,1]])
         self.R_y = np.matrix([[cos(pi/2),0,-sin(pi/2),0],[0,1,0,0],[sin(pi/2),0,cos(pi/2),0],[0,0,0,1]])

         matrix = self.R_x*self.R_y
         
         quat_arrow = tft.quaternion_from_matrix(matrix) #self.theta[i])

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

         self.pub.publish(self.cyl_2)

         self.pub.publish(self.sph)

         self.th = self.data_in.theta 
 
         # input cylinder dynamics here
         self.R_z = np.matrix([[cos(self.th),sin(self.th),0,0],[-sin(self.th),cos(self.th),0,0],[0,0,1,0],[0,0,0,1]])
      
         self.cyl.pose.position.x = 0.0
         self.cyl.pose.position.y = 0.0
         self.cyl.pose.position.z = 20.0 - 4

         x_cyl = float(self.cyl.pose.position.x)
         y_cyl = float(self.cyl.pose.position.y)
         z_cyl = float(self.cyl.pose.position.z)

         pos_cyl = np.matrix([[x_cyl],[y_cyl],[z_cyl],[1]])

         pos_cyl_new = self.R_z*self.R_y*pos_cyl

         self.cyl.pose.position.x = pos_cyl_new[0]
         self.cyl.pose.position.y = pos_cyl_new[1]
         self.cyl.pose.position.z = pos_cyl_new[2]      

         matrix_cyl = self.R_z*self.R_y

         quat_cyl = tft.quaternion_from_matrix(matrix_cyl)

         self.cyl.pose.orientation.x = quat_cyl[0]
         self.cyl.pose.orientation.y = quat_cyl[1]
         self.cyl.pose.orientation.z = quat_cyl[2]
         self.cyl.pose.orientation.w = quat_cyl[3]
         

         self.pub.publish(self.cyl)

         for i in range(0,12):

            # self.R_x needs to be updated every i
            self.R_x = np.matrix([[1,0,0,0],[0,cos(self.theta[i]),sin(self.theta[i]),0],[0,-sin(self.theta[i]),cos(self.theta[i]),0],[0,0,0,1]])

            matrix = self.R_z*self.R_x*self.R_y
            
            self.arrow_array[i].scale.x = 10.0*self.data_in.force[i]/6.0 + 0.3
            self.arrow_array[i].color.r = self.data_in.force[i]/12.0
            if i == 0 or i == 1 or i == 2 or i == 9 or i == 10 or i == 11:
               self.arrow_array[i].pose.position.x = -6 - 9
            if i == 3 or i == 4 or i == 5 or i == 6 or i == 7 or i == 8:
               self.arrow_array[i].pose.position.x = -16 - 9
            self.arrow_array[i].pose.position.y = -(8.5 + self.arrow_array[i].scale.x)*sin(self.theta[i])
            self.arrow_array[i].pose.position.z = -(8.5 + self.arrow_array[i].scale.x)*cos(self.theta[i])

            x = float(self.arrow_array[i].pose.position.x)
            y = float(self.arrow_array[i].pose.position.y)
            z = float(self.arrow_array[i].pose.position.z)

            pos = np.matrix([[x],[y],[z],[1]])

            pos_new = self.R_z*pos

            self.arrow_array[i].pose.position.x = pos_new[0] 
            self.arrow_array[i].pose.position.y = pos_new[1]
            self.arrow_array[i].pose.position.z = pos_new[2]

            quat_arrow = tft.quaternion_from_matrix(matrix)
            
            self.arrow_array[i].pose.orientation.x = quat_arrow[0]
            self.arrow_array[i].pose.orientation.y = quat_arrow[1]
            self.arrow_array[i].pose.orientation.z = quat_arrow[2]
            self.arrow_array[i].pose.orientation.w = quat_arrow[3]

            self.pub.publish(self.arrow_array[i])
         self.rate.sleep()

if __name__=='__main__':
   

   # initialize a ROS node for the markers
   rospy.init_node('markers', anonymous=True)

   visualize = tactile_visualization()

   visualize.run()

