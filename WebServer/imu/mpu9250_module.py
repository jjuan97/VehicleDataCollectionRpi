import os
import sys
import time
import smbus

from imusensor.MPU9250 import MPU9250

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()
#print("start")
#imu.caliberateMagApprox()
imu.loadCalibDataFromFile("./imu/calib.json")
print("IMU: calibration data loaded")

def read_data():
	imu.readSensor()
	imu.computeOrientation()
		
	# Sensors values in ENU convention
	ax = imu.AccelVals[1]
	ay = imu.AccelVals[0]
	az = -imu.AccelVals[2]
	gx = imu.GyroVals[1]
	gy = imu.GyroVals[0]
	gz = -imu.GyroVals[2]
	mx = imu.MagVals[1]
	my = imu.MagVals[0]
	mz = -imu.MagVals[2]
	
	return ((ax,ay,az), (gx,gy,gz), (mx,my,mz))

def print_data(num: int = 100):
	while True:
		imu.readSensor()
		imu.computeOrientation()
		# Sensors values in ENU convention
		ax = imu.AccelVals[1]
		ay = imu.AccelVals[0]
		az = -imu.AccelVals[2]
		gx = imu.GyroVals[1]
		gy = imu.GyroVals[0]
		gz = -imu.GyroVals[2]
		mx = imu.MagVals[1]
		my = imu.MagVals[0]
		mz = -imu.MagVals[2]
		print ("Accel x: {0} ; Accel y : {1} ; Accel z : {2} (m/s^2)".format(ax, ay, az))
		print ("Gyro x: {0} ; Gyro y : {1} ; Gyro z : {2} (rad/seg)".format(gx, gy, gz))
		print ("Mag x: {0} ; Mag y : {1} ; Mag z : {2} (?)".format(mx, my, mz))
		time.sleep(0.1)
		
if __name__ == "__main__":
	print_data()
