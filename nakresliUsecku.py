from machine import Pin, PWM
from time import sleep, sleep_ms
from math import sqrt, acos, atan2, pi, degrees

servo1 = PWM(Pin(0))
servo1.freq(50)
servo2 = PWM(Pin(1))
servo2.freq(50)
servo3 = PWM(Pin(2))
servo3.freq(50)

dutymin = 3277-1300
dutymax = 6554+1300
dutyavg = int((dutymin+dutymax)/2)
servo1.duty_u16(dutyavg)
servo2.duty_u16(dutyavg)
servo3.duty_u16(dutyavg)


a1 = 10.5 # delka prvniho ramene
a2 = 6.5 # delka druheho ramene


def inverzniKinematika(x1,x2):
    xSquare = x1*x1+x2*x2
    xNorm = sqrt(xSquare)
    if xNorm>a1+a2 or xNorm<abs(a1-a2):
        print("Error xNorm!")
        return None
    alfa = acos((xSquare+a1*a1-a2*a2)/(2*a1*xNorm))
    beta = acos((a1*a1+a2*a2-xSquare)/(2*a1*a2))
    gama = atan2(x2,x1)
    theta1 = gama+alfa
    if abs(theta1)>pi/2:
        print("Error theta1!")
        return None
    theta2 = beta-pi
    if abs(theta2)>pi/2:
        print("Error theta2!")
        return
    return theta1, theta2

def nastavServa(theta1,theta2):
    servo1.duty_u16(int(dutyavg+(theta1/(pi/2))*(dutymax-dutyavg)))
    servo2.duty_u16(int(dutyavg+(theta2/(pi/2))*(dutymax-dutyavg)))
                    

x = a1+a2/2
steps = 200
while True:
    for i in range(-steps,steps,1):
        y = 6*(i/steps)
        theta1, theta2 = inverzniKinematika(x,y)
        nastavServa(theta1,-theta2)
        sleep_ms(10)
    for i in range(steps,-steps,-1):
        y = 6*(i/steps)
        theta1, theta2 = inverzniKinematika(x,y)
        nastavServa(theta1,-theta2)
        sleep_ms(10)
