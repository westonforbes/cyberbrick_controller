from machine import ADC, Pin
import time

# Define all six ADC-capable pins used on ESP32
adc_pins = [ADC(Pin(i)) for i in (0, 1, 2, 3, 4, 5)]

# Apply attenuation for full-scale voltage support (11 dB)
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

while True:
    scaled_values = [scale_input(adc.read_u16(), invert=True) for adc in adc_pins]
    print("DATA: " + ",".join(f"{val:4d}" for val in scaled_values))
    time.sleep(0.2)

