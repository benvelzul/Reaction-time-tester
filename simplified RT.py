# Pico Reaction Time Game (simplified)
import utime
import random
from machine import Pin, PWM

red_led = Pin(6, Pin.OUT)
yellow_led = Pin(7, Pin.OUT)
green_led = Pin(8, Pin.OUT)
button = Pin(16, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(15))
buzzer.duty_u16(0)  # Start silent

def lights_off():
    red_led.value(0)
    yellow_led.value(0)
    green_led.value(0)

def beep(duration=0.1, freq=1000):
    buzzer.freq(freq)
    buzzer.duty_u16(32768)  # 50% duty cycle
    utime.sleep(duration)
    buzzer.duty_u16(0)      # Silent (don't deinit)

def traffic_countdown():
    lights_off()
    red_led.value(1)
    utime.sleep(1)
    yellow_led.value(1)
    utime.sleep(1)

def run_game():
    lights_off()
    print("Press button to start...")
    last_btn = 1
    while True:
        btn = button.value()
        if btn == 0 and last_btn == 1:
            traffic_countdown()
            delay = random.uniform(2, 5)
            start_wait = utime.ticks_ms()
            while utime.ticks_diff(utime.ticks_ms(), start_wait) < int(delay * 1000):
                if button.value() == 0:
                    print("FALSE START!")
                    beep(0.2, freq=400)   # Low tone for false start
                    break
                utime.sleep(0.01)
            else:
                green_led.value(1)
                beep(0.05, freq=1500)     # High tone for GO
                start_time = utime.ticks_ms()
                while button.value() == 1:
                    utime.sleep(0.001)
                reaction = utime.ticks_diff(utime.ticks_ms(), start_time)
                print("Reaction Time:", reaction, "ms")
                beep(0.2, freq=1000)      # Medium tone for result
            last_btn = btn
        last_btn = btn
        utime.sleep(0.01)

run_game()