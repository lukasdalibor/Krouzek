from machine import Pin, I2C, PWM
import utime
import MPU6050
import math
import time
import ssd1306

P = 800
D = 100

motorRG = PWM(Pin(0))
motorRG.freq(50)
motorRGDuty = 0
motorRG.duty_u16(motorRGDuty)
motorBW = PWM(Pin(1))
motorBW.freq(50)
motorBWDuty = 0
motorBW.duty_u16(motorBWDuty)


led = Pin(25,Pin.OUT)
led.value(0)
button = Pin(2,Pin.IN,Pin.PULL_UP)
while button.value()==1:
    continue

#OLED display
i2coled = I2C(1, scl=Pin(19), sda=Pin(18))
oled = ssd1306.SSD1306_I2C(128, 64, i2coled)

# yellow: SCL on GP17 (pin 22), blue: SDA on GP16 (pin 21)
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 100000)
mpu = MPU6050.MPU6050(i2c)
mpu.wake()

dt = 10
alpha = 0.96

avgAccel = [0.0,0.0,0.0]
for i in range(2000):
    accel = mpu.read_accel_data()
    avgAccel[0] += accel[0]/2000
    avgAccel[1] += accel[1]/2000
    avgAccel[2] += accel[2]/2000
accelX = avgAccel[0] / math.sqrt(accel[0]*accel[0]+accel[1]*accel[1]+accel[2]*accel[2])
accelY = avgAccel[1]
accelZ = avgAccel[2]
lastPhiDeg = math.atan(accelY/accelZ)*180.0/math.pi
lastThetaDeg = math.atan(avgAccel[0]/avgAccel[2])*180.0/math.pi #math.asin(accelX)*180.0/math.pi

led.value(1)

dutyBase = 10000
motorRGDuty = dutyBase
motorRG.duty_u16(motorRGDuty)
motorBWDuty = dutyBase
motorBW.duty_u16(motorBWDuty)

lastt = time.ticks_ms()
utime.sleep_ms(dt)

while True:
    # data acquisition: unit gravity vector and body-frame rates [deg/s]
    accel = mpu.read_accel_data()
    gyro = mpu.read_gyro_data()
    t = time.ticks_ms()
    
    # accelerometer data processing: Euler angles
    accelX = accel[0] / math.sqrt(accel[0]*accel[0]+accel[1]*accel[1]+accel[2]*accel[2])
    accelY = accel[1]
    accelZ = accel[2]
    phi = math.atan(accelY/accelZ)
    phiDeg = phi*180.0/math.pi
    theta = math.atan(accel[0]/accel[2]) #math.asin(accelX)
    thetaDeg = theta*180.0/math.pi
    
    # gyroscope data processing: body-frame rates to Euler rates
    p = gyro[0]
    q = -gyro[1]
    r = -gyro[2]
    sphi = math.sin(phi)
    cphi = math.cos(phi)
    ttheta = math.tan(theta)
    phiDegDot = p + ttheta*(sphi*q + cphi*r)
    thetaDegDot = q #cphi*q-sphi*r

    # sensor fusion: complementary filter
    phiDeg = (1.0-alpha)*phiDeg + alpha*(lastPhiDeg+phiDegDot*(t-lastt)/1000)
    thetaDeg = (1.0-alpha)*thetaDeg + alpha*(lastThetaDeg+thetaDegDot*(t-lastt)/1000)
    lastPhiDeg = phiDeg
    lastThetaDeg = thetaDeg
    print(thetaDeg)
    
    u = math.floor(P*thetaDeg+D*thetaDegDot)
    motorRGDuty = dutyBase-u
    if motorRGDuty<0:
        motorRGDuty = 0
    elif motorRGDuty>65535:
        motorRGDuty = 65535
    motorBWDuty = dutyBase+u
    if motorBWDuty<0:
        motorBWDuty = 0
    elif motorBWDuty>65535:
        motorBWDuty = 65535
    #print(motorRGDuty,motorBWDuty)    
    motorRG.duty_u16(motorRGDuty)
    motorBW.duty_u16(motorBWDuty)

    theta = thetaDeg * math.pi/180.0
    st = math.sin(theta)
    ct = math.cos(theta)

    oled.fill(0)
    oled.text(str(motorRGDuty),0,0,1)
    oled.text(str(motorBWDuty),64,0,1)
    oled.draw_line(64-math.floor(64*ct),32-math.floor(64*st),64+math.floor(64*ct),32+math.floor(64*st),1)
    oled.show()
    
    lastt = t
    utime.sleep_ms(dt)
    
    if button.value()==0:
        break    
    
led.value(0)
motorRGDuty = 0
motorRG.duty_u16(motorRGDuty)
motorBWDuty = 0
motorBW.duty_u16(motorBWDuty)
