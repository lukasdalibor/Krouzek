from math import sqrt, acos, pi, cos, sin, atan, asin
from machine import PWM, Pin
import sys
from time import sleep

a0 = 7.65-3	# vyska ramenniho kloubu od stolu [cm]
a1 = 10.52	# delka ramene mezi ramennim a loketnim kloubem [cm]
a2 = 6.67	# delka ramene mezi loktem a zapestim1 [cm]
a3 = 19#17.58	# delka ramene mezi zapestim1 a konecky natazenych prstu [cm]

# robot A
serva = [0,0,0,0,0,0]
servaPrumery = [4850,5010,5100,4690,4600,4550]
serva90 = [8050,2110,8180,7760,7800,5150]

def inverzniKinematika(x,z,phi):
    A0 = a0-z
    xA = sqrt((a3-a1)**2+a2**2-A0**2)
    xC = a1+sqrt(a2**2+a3**2-A0**2)
    print(xA,xC)
    if x>=xA and x<=xC:
        r = sqrt((x*a3-A0*a2)**2+(x*a2+A0*a3)**2)
        rho = atan((x*a2+A0*a3)/(x*a3-A0*a2))
        phi = rho + pi - asin((x**2+A0**2+a2**2+a3**2-a1**2)/2.0/r)
        phi -= 10*pi/180
        print(180*phi/pi)

    x2 = x - a3*cos(pi/2-phi)
    z2 = z - a3*sin(pi/2-phi)
    c = sqrt(x2*x2+(z2-a0)*(z2-a0))
    if z2-a0>=0:
        delta = acos(x2/c)
    else:    
        delta = -acos(x2/c)
    cosTheta2 = (c*c-a1*a1-a2*a2)/2/a1/a2
    if abs(cosTheta2)>1:
        print(f"Nedosazitelny bod: cos(theta2)={cosTheta2}")
        #return
    theta2 = acos(cosTheta2)
    cosAlpha = (c*c+a1*a1-a2*a2)/2/a1/c
    if abs(cosAlpha)>1:
        print(f"Nedosazitelny bod: cos(alpha)={cosAlpha}")
        #return
    alpha = acos(cosAlpha)
    theta1 = pi/2-delta-alpha
    theta3 = phi-theta1-theta2
    theta1Stupne = 180*theta1/pi
    theta2Stupne = 180*theta2/pi
    theta3Stupne = 180*theta3/pi
    if abs(theta1)>pi/2:
        print(f"Nedosazitelny bod: theta1={theta1Stupne}")
        #return
    if abs(theta2)>pi/2:
        print(f"Nedosazitelny bod: theta2={theta2Stupne}")
        #return
    if abs(theta3)>pi/2:
        print(f"Nedosazitelny bod: theta3={theta3Stupne}")
        #return
    print(theta1Stupne,theta2Stupne,theta3Stupne)
    return theta1, theta2, theta3
    
def go(dt):
    maxZmena = 0
    for i in range(6):
        zmena = abs(novaPoloha[i]-staraPoloha[i])
        if zmena>maxZmena:
            maxZmena = zmena
    for i in range(maxZmena):
        s = i/(maxZmena-1)
        for j in range(6):
            serva[j].duty_u16(int(staraPoloha[j]+s*(novaPoloha[j]-staraPoloha[j])))
        sleep(dt/maxZmena)        
    
theta1, theta2, theta3 = inverzniKinematika(20,5,96*pi/180)
print(theta1,theta2,theta3)
#sleep(20000)

staraPoloha = servaPrumery.copy()
staraPoloha[4] = serva90[4]
novaPoloha = staraPoloha.copy()
for i in range(6):
    serva[i] = PWM(Pin(i))
    serva[i].freq(50)
    serva[i].duty_u16(staraPoloha[i])
print("STARA POLOHA:")
print(staraPoloha)
sleep(1)

z = 2
A0 = a0-z
xA = sqrt((a3-a1)**2+a2**2-A0**2)
xC = a1+sqrt(a2**2+a3**2-A0**2)
for x in range(xA,xC,3):
    theta1, theta2, theta3 = inverzniKinematika(x,2,96*pi/180)
    novaPoloha[1] = int(servaPrumery[1]+(theta1/(pi/2))*(serva90[1]-servaPrumery[1])) #*servaRozsahy[1])
    novaPoloha[2] = int(servaPrumery[2]+(theta2/(pi/2))*(serva90[2]-servaPrumery[2])) #*servaRozsahy[2])
    novaPoloha[3] = int(servaPrumery[3]+(theta3/(pi/2))*(serva90[3]-servaPrumery[3])) #*servaRozsahy[3])
    print("x: NOVA POLOHA:")
    print(x,": ",novaPoloha)
    go(1)
    sleep(3)
    for i in range(6):
        staraPoloha[i] = novaPoloha[i]

for j in range(1,4):
    novaPoloha[j] = servaPrumery[j]
go(1)

sleep(10)
