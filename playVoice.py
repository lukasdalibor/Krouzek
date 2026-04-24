from machine import Pin, Timer
import rp2
from rp2 import StateMachine
import math
from time import sleep


@rp2.asm_pio(
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    sideset_init=rp2.PIO.OUT_LOW,
    autopull=True,
    fifo_join=rp2.PIO.JOIN_TX)
def pwmDAC():
    wrap_target()
    
    out(x,4).side(0)
    set(y,0x10)

    label("low")
    jmp(y_dec,"cmp")
    label("cmp")
    jmp(x_not_y,"low")
    
    nop().side(1)[1]
    label("high")
    jmp(y_dec,"high")[1]
    
    wrap()


TX_PIN = 16
maxfreq = 13_500_000
freq = 13_500_000
freq = 5_000_000
smTX = StateMachine(0, pwmDAC, freq=freq, sideset_base=Pin(TX_PIN))

# triangle signal
up = [i * 0x11111111 for i in range(16)]
#down = [i * 0x11111111 for i in range(14, 0, -1)]
#triangle = up + down

N = 100
sine = [
    round((math.sin(2 * math.pi * i / N) + 1) / 2 * 15)
    for i in range(N)
]
    
square = [0 for _ in range(N//2)] + [15 for _ in range(N//2)]

#organ = [7, 15, 13, 11, 10, 7, 6, 7, 8, 9, 9, 8, 6, 6, 7, 7, 8, 8, 6, 5, 5, 6, 7, 8, 7, 4, 3, 1, 0, 7]
organ = [7, 10, 12, 14, 15, 14, 14, 13, 12, 12, 11, 11, 10, 10, 9, 8, 7, 7, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 8, 8, 8, 7, 7, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 7, 7, 6, 6, 6, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 7, 7, 6, 5, 4, 4, 3, 3, 2, 2, 1, 0, 0, 0, 0, 2, 4, 7]

violin = [7, 9, 11, 12, 14, 14, 15, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 12, 12, 12, 12, 11, 11, 10, 10, 9, 9, 9, 8, 8, 8, 7, 7, 6, 6, 6, 5, 5, 5, 4, 4, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 3, 5, 7]

trumpet = [7, 13, 15, 12, 9, 8, 10, 11, 11, 10, 10, 11, 12, 12, 11, 11, 11, 12, 11, 11, 11, 11, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 3, 3, 2, 2, 3, 4, 4, 3, 3, 4, 6, 5, 2, 0, 1, 7]

voice = [8, 7, 7, 7, 6, 5, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11, 11, 11, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 12, 12, 12, 12, 12, 11, 11, 11, 10, 10, 10, 9]

voice2 = [3, 4, 4, 4, 4, 4, 5, 5, 5, 6, 9, 11, 13, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 14, 14, 14, 13, 13, 13, 12, 11, 11, 10, 9, 8, 7, 6, 4, 3, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 10, 11, 11, 12, 12, 12, 12, 12, 12, 11, 11, 10, 10, 9, 8, 7, 7, 7, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 11, 11, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 12, 12, 12, 11, 10, 9, 8, 8, 7, 6, 6, 5, 5, 5, 5, 4, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 8, 9, 9, 10, 11, 12, 12, 13, 13, 13, 13, 13, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 9, 9, 10, 11, 12, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 13, 12, 12, 12, 12, 11, 11, 11, 11, 10, 10, 9, 9, 8, 8, 8, 7, 7, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 13, 13, 13, 13, 12, 10, 7, 3, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]

with open("data.txt","r") as f:
    datatmp = eval(f.read())
data = datatmp[80:230]
N = len(data)
mindata = min(data)
maxdata = max(data)
rangedata = maxdata-mindata
data16 = [0] * N
for i in range(N):
    data16[i] = min(int(16*((data[i]-mindata)/rangedata)),15)

instrument = data16
N = len(instrument)
print(N)
for i in range(N):
    instrument[i] = up[instrument[i]]

    
#for i in range(0,N,4):
#    print((sine[i] & 0xf),(square[i] & 0xf),(organ[i] & 0xf),(violin[i] & 0xf),(trumpet[i] & 0xf))
#    #print((violin[i] & 0xf))

#sleep(1000)

smTX.init(pwmDAC, freq=int(freq*N/100), sideset_base=Pin(TX_PIN))
smTX.active(1)

def update(timer):
    global freq, maxfreq
    if freq<maxfreq:
        freq = int(2.0**(1.0/12.0) * freq)
        smTX.active(0)
        smTX.init(pwmDAC, freq=freq, sideset_base=Pin(TX_PIN))
        smTX.active(1)
        print(freq)
    else:
        smTX.active(0)

#tim = Timer()
#tim.init(period=1000, mode=Timer.PERIODIC, callback=update)

while True:
    for w in instrument:
        #for j in range(2):
            smTX.put(w)