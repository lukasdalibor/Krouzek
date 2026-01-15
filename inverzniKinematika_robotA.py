from math import sqrt, acos, pi, cos, sin, atan, asin, atan2
from machine import PWM, Pin
import sys
from time import sleep

a0 = 7.65	# vyska ramenniho kloubu od stolu [cm]
a1 = 10.52	# delka ramene mezi ramennim a loketnim kloubem [cm]
a2 = 6.67	# delka ramene mezi loktem a zapestim1 [cm]
a3 = 19#17.58	# delka ramene mezi zapestim1 a konecky natazenych prstu [cm]

# robot A
serva = [0,0,0,0,0,0]
servaPrumery = [4850,5010,5100,4690,4600,4550]
serva90 = [8050,2110,8180,7760,7800,6550] #7550]

def inverzniKinematika(xx,y,z,phi):
    theta0 = atan2(y,xx)
    x = sqrt(xx*xx+y*y)
    A0 = a0-z
    xA = sqrt((a3-a1)**2+a2**2-A0**2)
    xC = a1+sqrt(a2**2+a3**2-A0**2)
    print("xA=",xA,", xC=",xC,", x=",x)
    if x>=xA and x<=xC:
        r = sqrt((x*a3-A0*a2)**2+(x*a2+A0*a3)**2)
        rho = atan((x*a2+A0*a3)/(x*a3-A0*a2))
        phi = rho + pi - asin((x**2+A0**2+a2**2+a3**2-a1**2)/2.0/r)
        #phi -= 10*pi/180
        print("Sklon prstu: ",180*phi/pi)

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
    if abs(theta1)>1.01*pi/2:
        print(f"Nedosazitelny bod: theta1={theta1Stupne}")
        #return
    if abs(theta2)>1.01*pi/2:
        print(f"Nedosazitelny bod: theta2={theta2Stupne}")
        #return
    if abs(theta3)>1.01*pi/2:
        print(f"Nedosazitelny bod: theta3={theta3Stupne}")
        #return
    print(theta1Stupne,theta2Stupne,theta3Stupne)
    return theta0,theta1, theta2, theta3
    
def go(pose0,pose1,dt):
    maxZmena = 0
    for i in range(6):
        zmena = abs(pose1[i]-pose0[i])
        if zmena>maxZmena:
            maxZmena = zmena
    for i in range(maxZmena):
        s = i/(maxZmena-1)
        for j in range(6):
            serva[j].duty_u16(int(pose0[j]+s*(pose1[j]-pose0[j])))
        sleep(dt/maxZmena)        
    
initPoseOff = servaPrumery.copy()
initPoseOff[4] = servaPrumery[4]+0*(serva90[4]-servaPrumery[4])
initPoseOff[5] = servaPrumery[5]+0*(serva90[5]-servaPrumery[5])
initPoseOn = initPoseOff.copy()
initPoseOn[5] = servaPrumery[5]+1*(serva90[5]-servaPrumery[5])
for i in range(6):
    serva[i] = PWM(Pin(i))
    serva[i].freq(50)
    serva[i].duty_u16(initPoseOff[i])

theta0, theta1, theta2, theta3 = inverzniKinematika(0,10,0.5,0)
takePoseOff = initPoseOff.copy()
takePoseOff[0] = int(servaPrumery[0]+(theta0/(pi/2))*(serva90[0]-servaPrumery[0])) #*servaRozsahy[0])
takePoseOff[1] = int(servaPrumery[1]+(theta1/(pi/2))*(serva90[1]-servaPrumery[1])) #*servaRozsahy[1])
takePoseOff[2] = int(servaPrumery[2]+(theta2/(pi/2))*(serva90[2]-servaPrumery[2])) #*servaRozsahy[2])
takePoseOff[3] = int(servaPrumery[3]+(theta3/(pi/2))*(serva90[3]-servaPrumery[3])) #*servaRozsahy[3])
takePoseOn = takePoseOff.copy()
takePoseOn[5] = servaPrumery[5]+1*(serva90[5]-servaPrumery[5])

theta0, theta1, theta2, theta3 = inverzniKinematika(0,10,2,0)
takeUpPoseOff = initPoseOff.copy()
takeUpPoseOff[0] = int(servaPrumery[0]+(theta0/(pi/2))*(serva90[0]-servaPrumery[0])) #*servaRozsahy[0])
takeUpPoseOff[1] = int(servaPrumery[1]+(theta1/(pi/2))*(serva90[1]-servaPrumery[1])) #*servaRozsahy[1])
takeUpPoseOff[2] = int(servaPrumery[2]+(theta2/(pi/2))*(serva90[2]-servaPrumery[2])) #*servaRozsahy[2])
takeUpPoseOff[3] = int(servaPrumery[3]+(theta3/(pi/2))*(serva90[3]-servaPrumery[3])) #*servaRozsahy[3])
takeUpPoseOn = takeUpPoseOff.copy()
takeUpPoseOn[5] = servaPrumery[5]+1*(serva90[5]-servaPrumery[5])

putPoseOff = [0,0,0,0,0,0,0]
putPoseOn = [0,0,0,0,0,0,0]
for i in range(0,7):
    y = (3-i)*4
    theta0, theta1, theta2, theta3 = inverzniKinematika(13,y,25-10,0)
    putPoseOff[i] = initPoseOff.copy()
    putPoseOff[i][0] = int(servaPrumery[0]+(theta0/(pi/2))*(serva90[0]-servaPrumery[0])) #*servaRozsahy[0])
    putPoseOff[i][1] = int(servaPrumery[1]+(theta1/(pi/2))*(serva90[1]-servaPrumery[1])) #*servaRozsahy[1])
    putPoseOff[i][2] = int(servaPrumery[2]+(theta2/(pi/2))*(serva90[2]-servaPrumery[2])) #*servaRozsahy[2])
    putPoseOff[i][3] = int(servaPrumery[3]+(theta3/(pi/2))*(serva90[3]-servaPrumery[3])) #*servaRozsahy[3])
    putPoseOn[i] = putPoseOff[i].copy()
    putPoseOn[i][5] = servaPrumery[5]+1*(serva90[5]-servaPrumery[5])

for i in range(0,7):
    go(initPoseOff,takeUpPoseOff,4)
    go(takeUpPoseOff,takePoseOff,2)
    go(takePoseOff,takePoseOn,2)
    go(takePoseOn,takeUpPoseOn,2)
    go(takeUpPoseOn,initPoseOn,4)
    go(initPoseOn,putPoseOn[i],4)
    go(putPoseOn[i],putPoseOff[i],2)
    go(putPoseOff[i],initPoseOff,4)

sleep(100)