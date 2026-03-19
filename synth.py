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


PIN0 = 16
basefreq = 13_500_000//4
tone = 0
freq0 = 13_500_000//4
sm0 = StateMachine(0, pwmDAC, freq=freq0, sideset_base=Pin(PIN0))
PIN1 = 17
freq1 = 13_500_000//4
sm1 = StateMachine(1, pwmDAC, freq=freq1, sideset_base=Pin(PIN1))

# triangle signal
up = [i * 0x11111111 for i in range(16)]
#down = [i * 0x11111111 for i in range(14, 0, -1)]
#triangle = up + down

N = 100
sine = [
    round((math.sin(2 * math.pi * i / N) + 1) / 2 * 15)
    #round((math.sin(8 * math.pi * i / N) + 1) / 2 * 15)
    #round((math.sin(8 * math.pi * i / N)+math.sin(4 * math.pi * i/N) + 2) / 4 * 15)
    for i in range(N)
]
    
square = [0 for _ in range(N//2)] + [15 for _ in range(N//2)]

#organ = [7, 15, 13, 11, 10, 7, 6, 7, 8, 9, 9, 8, 6, 6, 7, 7, 8, 8, 6, 5, 5, 6, 7, 8, 7, 4, 3, 1, 0, 7]
organ = [7, 10, 12, 14, 15, 14, 14, 13, 12, 12, 11, 11, 10, 10, 9, 8, 7, 7, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 8, 8, 8, 7, 7, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 7, 7, 6, 6, 6, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 7, 7, 6, 5, 4, 4, 3, 3, 2, 2, 1, 0, 0, 0, 0, 2, 4, 7]

violin = [7, 9, 11, 12, 14, 14, 15, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 12, 12, 12, 12, 11, 11, 10, 10, 9, 9, 9, 8, 8, 8, 7, 7, 6, 6, 6, 5, 5, 5, 4, 4, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 3, 5, 7]

trumpet = [7, 13, 15, 12, 9, 8, 10, 11, 11, 10, 10, 11, 12, 12, 11, 11, 11, 12, 11, 11, 11, 11, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 3, 3, 2, 2, 3, 4, 4, 3, 3, 4, 6, 5, 2, 0, 1, 7]

for i in range(N):
    organ[i] = up[organ[i]]
    sine[i] = up[sine[i]]
    square[i] = up[square[i]]
    violin[i] = up[violin[i]]
    trumpet[i] = up[trumpet[i]]

    
for i in range(0,N,4):
    print((sine[i] & 0xf),(square[i] & 0xf),(organ[i] & 0xf),(violin[i] & 0xf),(trumpet[i] & 0xf))

#sleep(1000)

sm0.active(1)
sm1.active(1)

def update(timer):
    global freq0, maxfreq, basefreq, tone
    if tone<14:
        tone += 1
        freq0 = int(2.0**(tone/12.0) * basefreq)
        sm0.active(0)
        sm0.init(pwmDAC, freq=freq0, sideset_base=Pin(PIN0))
        sm0.active(1)
        print(tone)
    else:
        sm0.active(0)

tim = Timer()
tim.init(period=5000, mode=Timer.PERIODIC, callback=update)

idx0 = 0
idx1 = 0
while True:
    if sm0.tx_fifo()<8:
        sm0.put(trumpet[idx0])
        idx0 = (idx0+1) % N
    if sm1.tx_fifo()<8:
        sm1.put(trumpet[idx1])
        idx1 = (idx1+1) % N
