from machine import Pin, PWM
from time import sleep

melody = ['C4','E4','G4','F4','E4','D4','C4','E4','G4','F4','E4','D4','E4','E4','D4','E4','F4','D4','E4','E4','D4','E4','F4','D4','E4','D4','C4']
lengths = [1,1,0.5,0.5,0.5,0.5,1,1,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,1,1,0.5,0.5,0.5,0.5,1,1,1,1,1]

notes = ['C', 'Cis', 'D', 'Dis', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Ais', 'H']
keys = [f"{note}{octave}"
        for octave in range(1, 6)
        for note in notes]
tones = [ int(55 * (2.0 ** (i / 12.0))) for i in range(-9,-9+5*12) ]
tonesByKeys = dict(zip(keys,tones))
    
buzzer = PWM(Pin(16,Pin.OUT))
for t,l in zip(melody,lengths):
    buzzer.duty_u16(32768)
    buzzer.freq(tonesByKeys[t])
    sleep(0.5*l)
    buzzer.duty_u16(0)
    sleep(0.01)