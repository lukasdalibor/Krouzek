from machine import Pin, Timer
from time import sleep

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

while True:
    for i in PINS:
        if state_changed[i]:
            print(f"Button {i} set to {last_state[i]}")
            state_changed[i] = False
    sleep(0.01)