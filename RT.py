# Pico Reaction Time Game with TM1637 display
import utime
import random
import tm1637
from machine import Pin, PWM

# ── Hardware setup ────────────────────────────────────────────────────────────
red_led    = Pin(6,  Pin.OUT)
yellow_led = Pin(7,  Pin.OUT)
green_led  = Pin(8,  Pin.OUT)
button     = Pin(16, Pin.IN, Pin.PULL_UP)
buzzer     = PWM(Pin(15))
buzzer.duty_u16(0)

display = tm1637.TM1637(clk=1, dio=0)
display.clear()

# ── Segment constants ─────────────────────────────────────────────────────────
SEG_GO   = [0x7d, 0x3f, 0x00, 0x00]
SEG_ERR  = [0x79, 0x50, 0x50, 0x00]
SEG_RDY  = [0x50, 0x5e, 0x5e, 0x6e]
SEG_DASH = [0x40, 0x40, 0x40, 0x40]

# ── Helpers ───────────────────────────────────────────────────────────────────
def lights_off():
    red_led.value(0); yellow_led.value(0); green_led.value(0)

def lights_on():
    red_led.value(1); yellow_led.value(1); green_led.value(1)

def beep(duration=0.1, freq=1000):
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    utime.sleep(duration)
    buzzer.duty_u16(0)

def traffic_countdown():
    lights_off()
    display.text(SEG_DASH)
    red_led.value(1)
    utime.sleep(1)
    lights_off()
    yellow_led.value(1)
    utime.sleep(1)
    lights_off()

# ── Main game loop ────────────────────────────────────────────────────────────
def run_game():
    lights_off()
    display.text(SEG_RDY)
    print("Press button to start...")
    last_btn = 1

    while True:
        btn = button.value()

        if btn == 0 and last_btn == 1:
            traffic_countdown()

            delay = random.uniform(1, 5)
            start_wait = utime.ticks_ms()
            false_start = False

            while utime.ticks_diff(utime.ticks_ms(), start_wait) < int(delay * 1000):
                if button.value() == 0:
                    false_start = True
                    break
                utime.sleep(0.01)

            if false_start:
                print("FALSE START!")
                display.text(SEG_ERR)
                beep(0.2, freq=400)
                lights_off()
                utime.sleep(1)
                display.text(SEG_RDY)

            else:
                lights_on()
                display.text(SEG_GO)
                beep(0.05, freq=1500)

                start_time = utime.ticks_ms()

                # ── Real-time chronometer ──────────────────────────────────
                # Display updates every ~50ms while counting up
                # Shows tenths of a second: e.g. 0.0 → 0001, 1.5 → 0015
                last_display_update = utime.ticks_ms()

                while button.value() == 1:
                    now = utime.ticks_ms()
                    # Update display every 50ms (20fps — fast enough, not too spammy)
                    if utime.ticks_diff(now, last_display_update) >= 50:
                        elapsed = utime.ticks_diff(now, start_time)
                        display.number(elapsed)
                        last_display_update = now
                    utime.sleep_ms(1)

                reaction = utime.ticks_diff(utime.ticks_ms(), start_time)
                print("Reaction Time:", reaction, "ms")

                # Freeze final time on display
                display.number(reaction)
                beep(0.2, freq=1000)

                lights_off()
                utime.sleep(2)
                display.text(SEG_RDY)

            last_btn = 0

        last_btn = btn
        utime.sleep(0.01)

run_game()
