from machine import Pin
import rp2
from rp2 import StateMachine
import math


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
smTX = StateMachine(0, pwmDAC, freq=8*857408, sideset_base=Pin(TX_PIN))

# triangle signal
up = [i * 0x11111111 for i in range(16)]
down = [i * 0x11111111 for i in range(14, 0, -1)]
triangle = up + down

N = 30
sine = [
    round((math.sin(2 * math.pi * i / N) + 1) / 2 * 15)
    for i in range(N)
]
    
square = [0 for _ in range(N//2)] + [15 for _ in range(N//2)]

for i in range(N):
    sine[i] = triangle[sine[i]]
    square[i] = triangle[square[i]]


smTX.active(1)
while True:
    for w in sine:
        for j in range(4):
            smTX.put(w)