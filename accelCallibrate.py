from machine import Pin, I2C
import utime
import MPU6050
import math
import time
import ssd1306

button = Pin(0,Pin.IN,Pin.PULL_UP)

# OLED
i2coled = I2C(1, scl=Pin(19), sda=Pin(18))
oled = ssd1306.SSD1306_I2C(128, 64, i2coled)

# Accel/gyro: yellow wire - SCL on GP17 (pin 22), blue wire - SDA on GP16 (pin 21)
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 100000)
mpu = MPU6050.MPU6050(i2c)
mpu.wake()

dt = 10
alpha = 0 #0.96

n = 20

# Callibrate at (0,0)
avgAccel = [0.0,0.0,0.0]
for i in range(n):
    accel = mpu.read_accel_data()
    avgAccel[0] += accel[0]/n
    avgAccel[1] += accel[1]/n
    avgAccel[2] += accel[2]/n
    print(avgAccel[0]*n/(i+1),avgAccel[1]*n/(i+1),avgAccel[2]*n/(i+1))
    time.sleep(0.5)
g = math.sqrt(accel[0]*accel[0]+accel[1]*accel[1]+accel[2]*accel[2])
accelX = avgAccel[0] / g
accelY = avgAccel[1]
accelZ = avgAccel[2]
lastPhiDeg = math.atan(accelY/accelZ)*180.0/math.pi
lastThetaDeg = math.asin(accelX)*180.0/math.pi
phiDeg0 = lastPhiDeg
thetaDeg0 = lastThetaDeg
print(phiDeg0,thetaDeg0)

while True:
    if button.value()==0:
        break

# Callibrate at (45,0)
avgAccel = [0.0,0.0,0.0]
for i in range(n):
    accel = mpu.read_accel_data()
    avgAccel[0] += accel[0]/n
    avgAccel[1] += accel[1]/n
    avgAccel[2] += accel[2]/n
    print(avgAccel[0]*n/(i+1),avgAccel[1]*n/(i+1),avgAccel[2]*n/(i+1))
    time.sleep(0.5)
g = math.sqrt(accel[0]*accel[0]+accel[1]*accel[1]+accel[2]*accel[2])
accelX = avgAccel[0] / g
accelY = avgAccel[1]
accelZ = avgAccel[2]
lastPhiDeg = math.atan(accelY/accelZ)*180.0/math.pi
lastThetaDeg = math.asin(accelX)*180.0/math.pi
phiDeg45 = lastPhiDeg
print(phiDeg45,lastThetaDeg)

while True:
    if button.value()==0:
        break

# Callibrate at (45,0)
avgAccel = [0.0,0.0,0.0]
for i in range(n):
    accel = mpu.read_accel_data()
    avgAccel[0] += accel[0]/n
    avgAccel[1] += accel[1]/n
    avgAccel[2] += accel[2]/n
    print(avgAccel[0]*n/(i+1),avgAccel[1]*n/(i+1),avgAccel[2]*n/(i+1))
    time.sleep(0.5)
g = math.sqrt(accel[0]*accel[0]+accel[1]*accel[1]+accel[2]*accel[2])
accelX = avgAccel[0] / g
accelY = avgAccel[1]
accelZ = avgAccel[2]
lastPhiDeg = math.atan(accelY/accelZ)*180.0/math.pi
lastThetaDeg = math.asin(accelX)*180.0/math.pi
thetaDeg45 = lastThetaDeg
print(lastPhiDeg,thetaDeg45)

while True:
    if button.value()==0:
        break

lastt = time.ticks_ms()
utime.sleep_ms(dt)

while True:
    # data acquisition: unit gravity vector and body-frame rates [deg/s]
    accel = mpu.read_accel_data()
    gyro = mpu.read_gyro_data()
    t = time.ticks_ms()
    
    # accelerometer data processing: Euler angles
    g = math.sqrt(accel[0]*accel[0]+accel[1]*accel[1]+accel[2]*accel[2])
    accelX = accel[0] / g
    accelY = accel[1]
    accelZ = accel[2]
    phi = math.atan(accelY/accelZ)
    phiDeg = phi*180.0/math.pi
    theta = math.asin(accelX)
    thetaDeg = theta*180.0/math.pi
    # correction
    phiDeg = (phiDeg-phiDeg0)*(45.0/phiDeg45)
    thetaDeg = (thetaDeg-thetaDeg0)*(45.0/thetaDeg45)
    
    # gyroscope data processing: body-frame rates to Euler rates
    p = gyro[0]
    q = -gyro[1]
    r = -gyro[2]
    sphi = math.sin(phi)
    cphi = math.cos(phi)
    ttheta = math.tan(theta)
    phiDegDot = p + ttheta*(sphi*q + cphi*r)
    thetaDegDot = cphi*q-sphi*r

    # sensor fusion: complementary filter
    phiDeg = (1.0-alpha)*phiDeg + alpha*(lastPhiDeg+phiDegDot*(t-lastt)/1000)
    thetaDeg = (1.0-alpha)*thetaDeg + alpha*(lastThetaDeg+thetaDegDot*(t-lastt)/1000)
    lastPhiDeg = phiDeg
    lastThetaDeg = thetaDeg
    print(phiDeg,thetaDeg)
    
    sp = math.sin(phi)
    cp = math.cos(phi)
    st = math.sin(theta)
    ct = math.cos(theta)
    i = [ct,0.0,-st]
    j = [sp*st,cp,sp*ct]
    k = [cp*st,-sp,cp*ct]
    ix = (i[0]-i[1])/math.sqrt(2.0)
    iy = (-i[0]-i[1]+2*i[2])/math.sqrt(6.0)
    jx = (j[0]-j[1])/math.sqrt(2.0)
    jy = (-j[0]-j[1]+2*j[2])/math.sqrt(6.0)
    kx = (k[0]-k[1])/math.sqrt(2.0)
    ky = (-k[0]-k[1]+2*k[2])/math.sqrt(6.0)
    oled.fill(0)
    oled.draw_line(64,32,math.floor(64+32*ix),math.floor(32+32*iy),1)
    oled.draw_line(64,32,math.floor(64+32*jx),math.floor(32+32*jy),1)
    oled.draw_line(64,32,math.floor(64+32*kx),math.floor(32+32*ky),1)
    oled.show()
    
    lastt = t
    utime.sleep_ms(dt)
