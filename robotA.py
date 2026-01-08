from machine import Pin, PWM
from time import sleep
import utime

serva = [0,0,0,0,0,0]
servaPrumery = [4850,5010,5100,4690,4600,4550]
serva90 = [8050,2110,8180,7760,7800,5150]
#servaRozsahy = [3150,3050,3000,3150,3100,1750]

for i in range(6):
    serva[i] = PWM(Pin(i))
    serva[i].freq(50)
    serva[i].duty_u16(servaPrumery[i])
serva[1].duty_u16(servaPrumery[i]-300)
serva[4].duty_u16(serva90[4])

buttonUP = Pin(12,Pin.IN,Pin.PULL_UP)
debounceTime = 500
lastUPTime = 0
buttonUPPressed = False
def buttonUPHandler(pin):
    global buttonUPPressed
    global lastUPTime
    currentTime = utime.ticks_ms()
    if utime.ticks_diff(currentTime,lastUPTime)>debounceTime:
        buttonUPPressed = True
buttonUP.irq(trigger=Pin.IRQ_FALLING,handler=buttonUPHandler)
buttonUp = Pin(13,Pin.IN,Pin.PULL_UP)
lastUpTime = 0
buttonUpPressed = False
def buttonUpHandler(pin):
    global buttonUpPressed
    global lastUpTime
    currentTime = utime.ticks_ms()
    if utime.ticks_diff(currentTime,lastUpTime)>debounceTime:
        buttonUpPressed = True
buttonUp.irq(trigger=Pin.IRQ_FALLING,handler=buttonUpHandler)
    
buttonDOWN = Pin(14,Pin.IN,Pin.PULL_UP)
lastDOWNTime = 0
buttonDOWNPressed = False
def buttonDOWNHandler(pin):
    global buttonDOWNPressed
    global lastDOWNTime
    currentTime = utime.ticks_ms()
    if utime.ticks_diff(currentTime,lastDOWNTime)>debounceTime:
        buttonDOWNPressed = True
buttonDOWN.irq(trigger=Pin.IRQ_FALLING,handler=buttonDOWNHandler)
buttonDown = Pin(15,Pin.IN,Pin.PULL_UP)
lastDownTime = 0
buttonDownPressed = False
def buttonDownHandler(pin):
    global buttonDownPressed
    global lastDownTime
    currentTime = utime.ticks_ms()
    if utime.ticks_diff(currentTime,lastDownTime)>debounceTime:
        buttonDownPressed = True
buttonDown.irq(trigger=Pin.IRQ_FALLING,handler=buttonDownHandler)

i = 5
val = servaPrumery[i]
print(val)

while True:
    if buttonUPPressed:
        val += 100
        print(val)
        serva[i].duty_u16(val)
        buttonUPPressed = False
    if buttonUpPressed:
        val += 10
        print(val)
        serva[i].duty_u16(val)
        buttonUpPressed = False
    if buttonDOWNPressed:
        val -= 100
        print(val)
        serva[i].duty_u16(val)
        buttonDOWNPressed = False
    if buttonDownPressed:
        val -= 10
        print(val)
        serva[i].duty_u16(val)
        buttonDownPressed = False
    sleep(0.1)
    

    
sleep(2000)

dt = 0.01
while True:
    for pozice in range(100):
        for i in range(0,6):
            duty = int(servaPrumery[i] + pozice*servaRozsahy[i]/100.0)
            serva[i].duty_u16(duty)
            print(duty)
            sleep(dt)
    for pozice in range(100,-100,-1):
        for i in range(0,6):
            duty = int(servaPrumery[i] + pozice*servaRozsahy[i]/100.0)
            serva[i].duty_u16(duty)
            print(duty)
            sleep(dt)
    for pozice in range(-100,0,1):
        for i in range(0,6):
            duty = int(servaPrumery[i] + pozice*servaRozsahy[i]/100.0)
            serva[i].duty_u16(duty)
            print(duty)
            sleep(dt)
            
      


while True:
    for duty in range(0,dutyMaxIncr,dutyIncr):
        zakladna.duty_u16(zakladnaDutyAvg+duty)
        rameno.duty_u16(ramenoDutyAvg+duty)
        loket.duty_u16(loketDutyAvg+duty)
        zapesti1.duty_u16(zapesti1DutyAvg+duty)
        zapesti2.duty_u16(zapesti2DutyAvg+duty)
        prsty.duty_u16(prstyDutyAvg+duty)
        #print(duty)
        sleep(dt)
    for duty in range(dutyMaxIncr,-dutyMinIncr,-dutyIncr):
        zakladna.duty_u16(zakladnaDutyAvg+duty)
        rameno.duty_u16(ramenoDutyAvg+duty)
        loket.duty_u16(loketDutyAvg+duty)
        zapesti1.duty_u16(zapesti1DutyAvg+duty)
        zapesti2.duty_u16(zapesti2DutyAvg+duty)
        prsty.duty_u16(prstyDutyAvg+duty)
        #print(duty)
        sleep(dt)
    for duty in range(-dutyMinIncr,0,dutyIncr):
        zakladna.duty_u16(zakladnaDutyAvg+duty)
        rameno.duty_u16(ramenoDutyAvg+duty)
        loket.duty_u16(loketDutyAvg+duty)
        zapesti1.duty_u16(zapesti1DutyAvg+duty)
        zapesti2.duty_u16(zapesti2DutyAvg+duty)
        prsty.duty_u16(prstyDutyAvg+duty)
        #print(duty)
        sleep(dt)
















zakladna = PWM(Pin(0))
zakladna.freq(50)
zakladna.duty_u16(zakladnaDutyAvg)
rameno = PWM(Pin(1))
rameno.freq(50)
rameno.duty_u16(ramenoDutyAvg)
loket = PWM(Pin(2))
loket.freq(50)
loket.duty_u16(loketDutyAvg)
zapesti1 = PWM(Pin(3))
zapesti1.freq(50)
zapesti1.duty_u16(zapesti1DutyAvg)
zapesti2 = PWM(Pin(4))
zapesti2.freq(50)
zapesti2.duty_u16(zapesti2DutyAvg)
prsty = PWM(Pin(5))
prsty.freq(50)
prsty.duty_u16(prstyDutyAvg)

sleep(2)

dutyIncr = 1
dutyMaxIncr = 500
dutyMinIncr = 500
dt = 0.001

while True:
    for duty in range(0,dutyMaxIncr,dutyIncr):
        zakladna.duty_u16(zakladnaDutyAvg+duty)
        rameno.duty_u16(ramenoDutyAvg+duty)
        loket.duty_u16(loketDutyAvg+duty)
        zapesti1.duty_u16(zapesti1DutyAvg+duty)
        zapesti2.duty_u16(zapesti2DutyAvg+duty)
        prsty.duty_u16(prstyDutyAvg+duty)
        #print(duty)
        sleep(dt)
    for duty in range(dutyMaxIncr,-dutyMinIncr,-dutyIncr):
        zakladna.duty_u16(zakladnaDutyAvg+duty)
        rameno.duty_u16(ramenoDutyAvg+duty)
        loket.duty_u16(loketDutyAvg+duty)
        zapesti1.duty_u16(zapesti1DutyAvg+duty)
        zapesti2.duty_u16(zapesti2DutyAvg+duty)
        prsty.duty_u16(prstyDutyAvg+duty)
        #print(duty)
        sleep(dt)
    for duty in range(-dutyMinIncr,0,dutyIncr):
        zakladna.duty_u16(zakladnaDutyAvg+duty)
        rameno.duty_u16(ramenoDutyAvg+duty)
        loket.duty_u16(loketDutyAvg+duty)
        zapesti1.duty_u16(zapesti1DutyAvg+duty)
        zapesti2.duty_u16(zapesti2DutyAvg+duty)
        prsty.duty_u16(prstyDutyAvg+duty)
        #print(duty)
        sleep(dt)