from machine import ADC, Pin
import neopixel
import time
import gc

print("Free heap:", gc.mem_free())
print("Used heap:", gc.mem_alloc())


# ADC and digital pins
adc_pins = [ADC(Pin(i)) for i in (0, 1, 2, 3, 4, 5)]
digital_pins = [Pin(i, Pin.IN, Pin.PULL_UP) for i in (6, 7, 21, 20)]

# Initialize NeoPixel (GPIO 13 is an example — change if needed)
np = neopixel.NeoPixel(Pin(8), 1)  # 1 NeoPixel on pin 13

# ADC attenuation
for adc in adc_pins:
    adc.atten(ADC.ATTN_11DB)

def scale_input(raw_value, in_range=(0, 65535), out_range=(-100, 100),
                deadband=5, trim=0, invert=False):
    in_min, in_max = in_range
    out_min, out_max = out_range

    scaled = ((raw_value - in_min) / (in_max - in_min)) * (out_max - out_min) + out_min
    out_mid = (out_min + out_max) / 2

    if abs(scaled - out_mid) < deadband:
        scaled = out_mid
    elif scaled > out_mid:
        scaled = ((scaled - out_mid - deadband) / (out_max - out_mid - deadband)) * (out_max - out_mid) + out_mid
    else:
        scaled = ((scaled - out_mid + deadband) / (out_min - out_mid + deadband)) * (out_min - out_mid) + out_mid

    if invert:
        scaled = out_max - (scaled - out_min)

    scaled += trim
    return int(round(max(out_min, min(out_max, scaled))))

# LED toggle state
cycle_count = 0
led_on = False

while True:
    scaled_values = [scale_input(adc.read_u16(), invert=True) for adc in adc_pins]
    digital_values = [1 - pin.value() for pin in digital_pins]

    print("|DATA|" + "|".join(f"{val:4d}" for val in scaled_values) +
          "|   " + "|   ".join(f"{val}" for val in digital_values) + "|")
    gc.collect()
    cycle_count += 1
    if cycle_count >= 100:
        led_on = not led_on
        if led_on:
            np[0] = (10, 10, 10)  # Bright white
        else:
            np[0] = (0, 0, 0)        # Off
        np.write()
        cycle_count = 0
    time.sleep_ms(5)

