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


with open("data.txt","w") as f:
    f.write(str(signal))