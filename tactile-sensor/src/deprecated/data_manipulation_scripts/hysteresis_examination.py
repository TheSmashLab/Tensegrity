#!/usr/bin/env python

import rospy
import numpy as np
from std_msgs.msg import String

class tactile_calibration():
	
	def __init__(self):
		self.num_of_taxels = 12
		self.sum = np.zeros(self.num_of_taxels)
		self.count = 0
		self.taxel_num = 0
		self.avg = np.array([])
		self.rate = 100 # 100 hz
		self.file_name = None
		self.record = None
		self.file = None
		self.taxel_readings = None
		self.taxel_array = np.array([])
		self.exit = True
		self.sample_size = 100
		self.sample_float = float(self.sample_size)

		rospy.Subscriber('chatter', String, self.data_callback, tcp_nodelay=False)
		
		

	def data_callback(self, String):
		self.taxel_readings = String.data
		self.taxel_array = np.fromstring(self.taxel_readings, count = self.num_of_taxels ,sep = ',')
		

		

	def average_data(self):
		self.count = self.count + 1
		self.sum = self.sum + self.taxel_array
		print(self.taxel_array)
		
		if self.count == self.sample_size:
			self.avg = self.sum/self.sample_float
			print(self.avg)		
			print(self.avg[self.taxel_num])
			print('Taxel ' + str(self.taxel_num + 1)) #+ ' complete: Move weight to next taxel'
			# self.taxel_num = self.taxel_num + 1
			response = input('Press any key to continue, press "n" to continue to next taxel\nor press "d" when finished')
			if response == 'd':
				self.exit = False
			else:
				if self.record:
					if response != "n":
						average = str(self.avg[self.taxel_num]) + ','
						self.file.write(average)
					else:
						average = str(self.avg[self.taxel_num])
						self.file.write(average)
			self.count = 0
			self.sum = 0
			self.avg = 0
			
                
                # This section has been commented out so that each taxel's hysteresis can be tested
		# if self.taxel_num == 6:
		# 	self.taxel_num = 5
		# 	if self.record:
		# 		self.file.write('\n')
                
			if response == 'n':
				self.file.write('\n')
				self.taxel_num = self.taxel_num + 1


			
			
			

	def init_record_data(self):
			
		self.record = input("Do you wish to record data? (y/n)\n")
		
		if self.record == 'y':
			self.record = True
			self.file_name = input("Please enter a file name: ")
			self.file = open(self.file_name,'w')
		else:
			self.record = False
			
		
		
		
	def shutdown(self):
		if self.record:
			self.file.close()
	
	
if __name__ == '__main__':

	rospy.init_node('listener', anonymous = True)
	
	Tcalibration = tactile_calibration()
	
	Tcalibration.init_record_data()
	
	rate = rospy.Rate(Tcalibration.rate)
	
	rospy.on_shutdown(Tcalibration.shutdown)
		
	while Tcalibration.exit:
		
		Tcalibration.average_data()
		
		rate.sleep()

# test comment
