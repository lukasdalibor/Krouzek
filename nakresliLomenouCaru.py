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
                    

def kresliLomenouCaru(body,steps=200,prodleva=10):
    """
    body     - seznam bodu [(x1,y1), (x2,y2), ...]
    steps    - pocet kroku na jednu usecku
    prodleva - prodleva mezi kroky v ms
    """
    for j in range(len(body)-1):
        x1, y1 = body[j]
        x2, y2 = body[j+1]
        for i in range(steps+1):
            t = i/steps
            x = x1 + (x2-x1)*t
            y = y1 + (y2-y1)*t
            theta1,theta2 = inverzniKinematika(x,y)
            nastavServa(theta1,-theta2)
            sleep_ms(prodleva)

def bezier(body,t):
    """
    vypocet bodu na Bezierove krivce.
    body - seznam ridicich bodu [(x1,y1), (x2,y2), ...]
    t    - parametr 0 az 1
    """
    body = list(body)
    while len(body) > 1:
        nove_body = []
        for i in range(len(body)-1):
            x = body[i][0]+(body[i+1][0]-body[i][0])*t
            y = body[i][1]+(body[i+1][1]-body[i][1])*t
            nove_body.append((x, y))
        body = nove_body
    return body[0]

def kresliBezierovuKrivku(body,steps=200,prodleva=10):
    for i in range(steps+1):
        t = i/steps
        x,y = bezier(body,t)
        theta1,theta2 = inverzniKinematika(x,y)
        nastavServa(theta1, -theta2)
        sleep_ms(prodleva)

x1 = a1+a2/4
x2 = a1+a2/2
x3 = a1+3*a2/4
y1 = 0
y2 = 3
y3 = 6
body = [(x1,-y3),(x3,-y2),(x2,y1),(x3,y2),(x1,y3),(x3,y2),(x2,y1),(x3,-y2),(x1,-y3)]
ridiciBody1 = [(x1,-y3),(x3,-y2),(x2,y1),(x3,y2),(x1,y3)]
ridiciBody2 = [(x1,y3),(x3,y2),(x2,y1),(x3,-y2),(x1,-y3)]

while True:
    kresliLomenouCaru(body)
    kresliBezierovuKrivku(ridiciBody1)
    kresliBezierovuKrivku(ridiciBody2)
