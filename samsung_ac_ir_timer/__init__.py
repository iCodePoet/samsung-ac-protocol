def decode_samsung_timers(bytes_arr):
    if len(bytes_arr) < 21:
        return None

    # 1. Extract Off-Timer (Byte 10 Lower Nibble + Byte 9 Upper Nibble)
    off_val = ((bytes_arr[10] & 0x0F) << 4) + (bytes_arr[9] >> 4)
    off_hours = 0.0
    if off_val > 0:
        off_hours = (off_val // 8) + (0.5 if off_val % 8 == 3 else 0.0)

    # 2. Extract On-Timer (Byte 11 Lower Nibble + Byte 10 Upper Nibble)
    on_val = ((bytes_arr[11] & 0x0F) << 4) + (bytes_arr[10] >> 4)
    on_hours = 0.0
    if on_val > 0:
        on_hours = (on_val // 8) + (0.5 if on_val % 8 == 3 else 0.0)

    return {
        "on_hours": on_hours,
        "off_hours": off_hours
    }
