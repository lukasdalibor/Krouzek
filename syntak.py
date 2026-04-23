from machine import ADC, Pin
import utime
from time import sleep
import rp2
from rp2 import StateMachine
import math

adc = ADC(Pin(26))

n = 800  # uprav dle RAM (~260k max teoreticky, ale opatrně)
signal = [0] * n  # předalokace = rychlejší

print("Start...")
start = utime.ticks_us()
for i in range(n):
    signal[i] = adc.read_u16()
end = utime.ticks_us()
print("Hotovo.")

# Výpočet reálné vzorkovací frekvence
elapsed_us = utime.ticks_diff(end, start)
fs = n * 1_000_000 / elapsed_us
print("Vzorkovací frekvence:", fs, "Hz")
sleep(1)

#Find global minimizer in the second quarter
idx1 = n//4
smin1 = signal[idx1]
for i in range(n//4,n//2):
    if signal[i]<smin1:
        idx1 = i
        smin1 = signal[idx1]
#Find global minimizer in the third quarter
idx2 = n//2
smin2 = signal[idx2]
for i in range(n//2,(3*n)//4):
    if signal[i]<smin2:
        idx2 = i
        smin2 = signal[idx2]

#DFT
N = idx2-idx1
real = [0.0] * N
imag = [0.0] * N
for i in range(idx1,idx2):
    real[i-idx1] = signal[i]
realmean = sum(real)/N
for i in range(N):
    real[i] -= realmean
print("Frequency (Hz) | Magnitude")
out_real = [0.0] * N
out_imag = [0.0] * N
for k in range(N // 2):  # only positive frequencies
    real_k = 0.0
    imag_k = 0.0
    for i in range(N):
        angle = -2 * math.pi * k * i / N
        c = math.cos(angle)
        s = math.sin(angle)
        real_k += real[i] * c
        imag_k += real[i] * s
    out_real[k] = real_k
    out_imag[k] = imag_k
#    mag = math.sqrt(real_k**2 + imag_k**2)
#    freq = k * fs / N
#    print(mag)
# mirror negative frequencies (optional for real signals)
for k in range(N // 2, N):
    out_real[k] = out_real[N - k - 1]
    out_imag[k] = -out_imag[N - k - 1]
# --- magnitude ---
mag = [0.0] * N
max_mag = 0.0
for k in range(N):
    m = math.sqrt(out_real[k]**2 + out_imag[k]**2)
    mag[k] = m
    if m > max_mag:
        max_mag = m
# --- threshold compression ---
threshold = 0.9
compress = N
for k in range(N):
    if mag[k] < threshold * max_mag:
        compress -= 1
        out_real[k] = 0.0
        out_imag[k] = 0.0
print("Compression by factor",compress/N)
sleep(10)
# --- reconstruction (inverse DFT) ---
recon = [0.0] * N
for n in range(N):
    val = 0.0
    for k in range(N):
        angle = 2 * math.pi * k * n / N
        val += out_real[k] * math.cos(angle) - out_imag[k] * math.sin(angle)
    recon[n] = val / N
#    print(recon[n])
#sleep(10000)


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

N = idx2-idx1
signal16 = [0]*N
recon16 = [0]*N
# Downscaling the signal to 0-0xf
rmin = min(recon)
rmax = max(recon)
rscale = rmax-rmin
for i in range(idx1,idx2):
    signal16[i-idx1] = signal[i] >> 12
    recon16[i-idx1] = min(int(16*((recon[i-idx1]-rmin)/rscale)),15)
    print(signal16[i-idx1],recon16[i-idx1])

# triangle signal
up = [i * 0x11111111 for i in range(16)]

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

instrument = signal16
N = len(instrument)
print(N)
for i in range(N):
    instrument[i] = up[instrument[i]]

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