from machine import Pin, PWM, Timer
from time import sleep

notes = ['C', 'Cis', 'D', 'Dis', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Ais', 'H']
keys = [f"{note}{octave}"
        for octave in range(1, 6)
        for note in notes]
tones = [ int(55 * (2.0 ** (i / 12.0))) for i in range(-9,-9+5*12) ]
tonesByKeys = dict(zip(keys,tones))

NUM_BUTTONS = 8
PINS = list(range(7,-1,-1))  # GPIO 0–7
DEBOUNCE_MS = 20

buttons = []
last_state = []
state_changed = []
debounce_timer = Timer()
pending = False

# Initialize buttons
for gpio in PINS:
    pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
    buttons.append(pin)
    last_state.append(pin.value())
    state_changed.append(False)

def process_buttons(timer):
    global pending

    for i, pin in enumerate(buttons):
        state = pin.value()
        if state!=last_state[i]:
            state_changed[i] = True
            last_state[i] = state

    pending = False

def button_irq(pin):
    global pending
    if not pending:
        pending = True
        debounce_timer.init(
            mode=Timer.ONE_SHOT,
            period=DEBOUNCE_MS,
            callback=process_buttons
        )

# Attach same IRQ handler to all buttons
for pin in buttons:
    pin.irq(
        trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
        handler=button_irq
    )

buzzer = PWM(Pin(16,Pin.OUT))

OCTAVE = 3
def tone(i):
    if i<3:
        return OCTAVE*12+2*i
    elif i<7:
        return OCTAVE*12+2*i-1
    else:
        return OCTAVE*12+12

while True:
    for i in PINS:
        if state_changed[i] and last_state[i]==1:
            print(f"Button {i} set to {last_state[i]}")
            state_changed[i] = False
            buzzer.duty_u16(0)
    for i in PINS:
        if state_changed[i] and last_state[i]==0:
            print(f"Button {i} set to {last_state[i]}")
            state_changed[i] = False
            state_changed[i] = False
            buzzer.duty_u16(32768)
            print(keys[tone(i)])
            buzzer.freq(tones[tone(i)])
    sleep(0.01)
