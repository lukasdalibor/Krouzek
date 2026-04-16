from machine import ADC, Pin
import utime
from time import sleep

adc = ADC(Pin(26))

n = 2000  # uprav dle RAM (~260k max teoreticky, ale opatrně)
signal = [0] * n  # předalokace = rychlejší
ncorr = 200
corr = [0] * ncorr

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
sleep(2)

# normalize signal to (0,1)
print("Normalize...")
smin = min(signal)
smax = max(signal)
srange = smax-smin
for i in range(n):
    signal[i] = (signal[i]-smin)/srange
    
# autokorelace
print("Autocorrelation...")
for lag in range(ncorr):
    s = 0
    for i in range(n-lag):
        s += signal[i] * signal[i+lag]
    corr[lag] = s
mincorr = min(corr)
maxcorr = max(corr)
corrRange = maxcorr-mincorr
for i in range(ncorr):
    corr[i] = (corr[i]-mincorr)/corrRange
#    print(signal[i],corr[i])
#sleep(200)

# najdi lokalni minimum
print("Find period...")
localMin = corr[0]
minLag = 0
for i in range(1,ncorr):
    if corr[i]<localMin:
        minLag = i
        localMin = corr[i]
    else:
        break
print(minLag)

# najdi periodu
localMax = corr[minLag]
period = minLag
for i in range(minLag+1,ncorr):
    if corr[i]>localMax:
        period = i
        localMax = corr[i]
    else:
        break
        
print("Period:",period)
sleep(2)
       
signal16 = [0]*period
for i in range(period):
    signal16[i] = min(int(16*signal[i]),15)
    print(16*signal[i],signal16[i])
    
sleep(10)

print("tisknu...")
print(signal16)
print("hotovo.")
sleep(1000)