import time
import board
import adafruit_mpu6050

i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = adafruit_mpu6050.MPU6050(i2c)

def read_data():
    return (mpu.acceleration, mpu.gyro, mpu.temperature)

def print_data(num: int = 10):
    for i in range(0, num):
        print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2"%(mpu.acceleration))
        print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s"%(mpu.gyro))
        print("Temperature: %.2f C"%mpu.temperature)
        print("")
        time.sleep(0.05)

if __name__ == "__main__":
    print_data()
