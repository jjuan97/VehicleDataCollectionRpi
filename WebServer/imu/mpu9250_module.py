from imu.mpu9250 import *
import time

time.sleep(1) # delay necessary to allow mpu9250 to settle

def read_data():
    ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
    mx,my,mz = AK8963_conv() # read and convert AK8963 magnetometer data
    return ((ax,ay,az), (wx,wy,wz), (mx,my,mz))
    
def print_data(num: int = 10):
    for i in range(0, num):
        ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
        mx,my,mz = AK8963_conv() # read and convert AK8963 magnetometer data
        print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2"%(ax,ay,az))
        print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s"%(wx,wy,wz))
        print("Magnetometer: X:%.2f, Y: %.2f, Z: %.2f uT"%(mx,my,mz))
        print("")

if __name__ == "__main__":
    print_data()
