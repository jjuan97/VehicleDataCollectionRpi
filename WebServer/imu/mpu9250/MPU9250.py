# this is to be saved in the local folder under the name "mpu9250_i2c.py"
# it will be used as the I2C controller and function harbor for the project 
# refer to datasheet and register map for full explanation

import smbus,time
from math import radians

# Config MPU6050 Ranges
range_accel_indx = 0 # 0 = ±2g, 1 = ±4g, 2 = ±8g and  3 = ±16g
range_gyro_indx = 0 # 0 = ±250°/s, 1 = ±500°/s, 2 = ±1000°/s and  3 = ±2000°/s

# AK8963 magnetometer sensitivity: 4900 uT
mag_sens = 4900.0

# Const values
STANDARD_GRAVITY = 9.80665

def MPU6050_start():
    # alter sample rate (stability)
    samp_rate_div = 0 # sample rate = 8 kHz/(1+samp_rate_div)
    bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, samp_rate_div)
    time.sleep(0.1)
    # reset all sensors
    bus.write_byte_data(MPU6050_ADDR,PWR_MGMT_1,0x00)
    time.sleep(0.1)
    # power management and crystal settings
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x01)
    time.sleep(0.1)
    #Write to Configuration register
    bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
    time.sleep(0.1)
    # Write to Gyro configuration register.
    # The MPU6050 can measure angular rotation using its on-chip gyroscope
    # with four programmable full scale ranges of ±250°/s, ±500°/s, ±1000°/s and ±2000°/s.
    gyro_config_vals = [250.0,500.0,1000.0,2000.0] # degrees/sec
    gyro_config_sel = [0b00000,0b010000,0b10000,0b11000] # byte registers
    bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, int(gyro_config_sel[range_gyro_indx]))
    time.sleep(0.1)
    # Write to Accel configuration register.
    # The MPU6050 can measure acceleration using its on-chip accelerometer
    # with four programmable full scale ranges of ±2g, ±4g, ±8g and ±16g.                        
    accel_config_vals = [2.0,4.0,8.0,16.0]
    accel_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
    bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, int(accel_config_sel[range_accel_indx]))
    time.sleep(0.1)
    # interrupt register (related to overflow of data [FIFO])
    bus.write_byte_data(MPU6050_ADDR, INT_ENABLE, 1)
    time.sleep(0.1)
    return gyro_config_vals[range_gyro_indx], accel_config_vals[range_accel_indx]
    
def read_raw_bits(register):
    # read accel and gyro values
    high = bus.read_byte_data(MPU6050_ADDR, register)
    low = bus.read_byte_data(MPU6050_ADDR, register+1)

    # combine higha and low for unsigned bit value
    value = ((high << 8) | low)
    
    # convert to +- value
    if(value > 32768):
        value -= 65536
    return value

def mpu6050_conv():
    """Return accelerometer and gyroscope values from MPU6050

    Returns:
    ax, ay, az: 3 axis accelerometer in m/s^2
    wx, wy, wz: 3 axis gyroscope in rad/seg
    """

    # raw acceleration bits
    acc_x = read_raw_bits(ACCEL_XOUT_H)
    acc_y = read_raw_bits(ACCEL_YOUT_H)
    acc_z = read_raw_bits(ACCEL_ZOUT_H)
    # raw gyroscope bits
    gyro_x = read_raw_bits(GYRO_XOUT_H)
    gyro_y = read_raw_bits(GYRO_YOUT_H)
    gyro_z = read_raw_bits(GYRO_ZOUT_H)

    # Check type of range and scale raw acceleration value
    if accel_range == 16.0: # Range 16g
        accel_scale = 2048
    if accel_range == 8.0:  # Range 8g
        accel_scale = 4096
    if accel_range == 4.0:  # Range 4g
        accel_scale = 8192
    if accel_range == 2.0:  # Range 2g
        accel_scale = 16384
    # Check type of range and scale raw gyroscope value
    if gyro_range == 250.0: # Range ±250°/s
        gyro_scale = 131
    if gyro_range == 500.0: # Range ±500°/s
        gyro_scale = 65.5
    if gyro_range == 1000.0: # Range ±1000°/s
        gyro_scale = 32.8
    if gyro_range == 2000.0: # Range ±2000°/s
        gyro_scale = 16.4
    
    # Setup range dependant scaling
    a_x = (acc_x / accel_scale) * STANDARD_GRAVITY
    a_y = (acc_y / accel_scale) * STANDARD_GRAVITY
    a_z = (acc_z / accel_scale) * STANDARD_GRAVITY

    w_x = radians(gyro_x / gyro_scale)
    w_y = radians(gyro_y / gyro_scale)
    w_z = radians(gyro_z / gyro_scale)

    return a_x, a_y, a_z, w_x, w_y, w_z

def AK8963_start():
    bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,0x00)
    time.sleep(0.1)
    AK8963_bit_res = 0b0001 # 0b0001 = 16-bit
    AK8963_samp_rate = 0b0110 # 0b0010 = 8 Hz, 0b0110 = 100 Hz
    AK8963_mode = (AK8963_bit_res <<4)+AK8963_samp_rate # bit conversion
    bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,AK8963_mode)
    time.sleep(0.1)
    
def AK8963_reader(register):
    # read magnetometer values
    low = bus.read_byte_data(AK8963_ADDR, register-1)
    high = bus.read_byte_data(AK8963_ADDR, register)
    # combine higha and low for unsigned bit value
    value = ((high << 8) | low)
    # convert to +- value
    if(value > 32768):
        value -= 65536
    return value

def AK8963_conv():
    # raw magnetometer bits

    loop_count = 0
    while 1:
        mag_x = AK8963_reader(HXH)
        mag_y = AK8963_reader(HYH)
        mag_z = AK8963_reader(HZH)

        # the next line is needed for AK8963
        if bin(bus.read_byte_data(AK8963_ADDR,AK8963_ST2))=='0b10000':
            break
        loop_count+=1
        
    #convert to acceleration in g and gyro dps
    m_x = (mag_x/(2.0**15.0))*mag_sens
    m_y = (mag_y/(2.0**15.0))*mag_sens
    m_z = (mag_z/(2.0**15.0))*mag_sens

    return m_x,m_y,m_z
    
# MPU6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
TEMP_OUT_H   = 0x41
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
#AK8963 registers
AK8963_ADDR   = 0x0C
AK8963_ST1    = 0x02
HXH          = 0x04
HYH          = 0x06
HZH          = 0x08
AK8963_ST2   = 0x09
AK8963_CNTL  = 0x0A

# start I2C driver
bus = smbus.SMBus(1) # start comm with i2c bus
gyro_range, accel_range = MPU6050_start() # instantiate gyro/accel
AK8963_start() # instantiate magnetometer
