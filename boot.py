from machine import ADC, Pin
import time

####USB####
# 5     2 #
# 4     1 #
# 3     0 #

# Setup the pins
left_joy = ADC(Pin(5))
right_joy = ADC(Pin(2))

# Set the attenuation to use the full voltage range. ESP32 quirk.
left_joy.atten(ADC.ATTN_11DB)
right_joy.atten(ADC.ATTN_11DB)

def scale_input(raw_value, in_range=(0, 65535), out_range=(-100, 100),
                deadband=5, trim=0, invert=False):
    """
    Scales an input from in_range to out_range, applies a deadband and trim.
    Optionally inverts the output.

    Parameters:
        raw_value (int/float): The raw input value.
        in_range (tuple): Input range as (min, max), default (0, 65535).
        out_range (tuple): Output range as (min, max), default (-100, 100).
        deadband (int): Deadband threshold around output midpoint (default = 5).
        trim (int): Trim adjustment applied after scaling (default = 0).
        invert (bool): If True, inverts the output direction (default = False).

    Returns:
        int: Scaled, deadbanded, trimmed, (optionally inverted) output.
    """

    in_min, in_max = in_range
    out_min, out_max = out_range

    # Step 1: Scale input
    scaled = ((raw_value - in_min) / (in_max - in_min)) * (out_max - out_min) + out_min

    # Step 2: Apply deadband around midpoint of output range
    out_mid = (out_min + out_max) / 2
    if abs(scaled - out_mid) < deadband:
        scaled = out_mid
    elif scaled > out_mid:
        scaled = ((scaled - out_mid - deadband) / (out_max - out_mid - deadband)) * (out_max - out_mid) + out_mid
    else:
        scaled = ((scaled - out_mid + deadband) / (out_min - out_mid + deadband)) * (out_min - out_mid) + out_mid

    # Step 3: Invert if needed
    if invert:
        scaled = out_max - (scaled - out_min)

    # Step 4: Apply trim and clamp to output range
    scaled += trim
    scaled = max(out_min, min(out_max, scaled))

    return int(round(scaled))



while True:
    # read a raw analog value in the range 0-65535
    left_joy_val = left_joy.read_u16()
    right_joy_val = right_joy.read_u16()

    left_scaled = scale_input(left_joy_val, invert=True)
    right_scaled = scale_input(right_joy_val, invert=True)
    print(f"left: {left_scaled:5.0f}, right: {right_scaled:5.0f}")
    
    time.sleep(0.2)


