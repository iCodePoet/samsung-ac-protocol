from typing import List, Dict, Optional

def decode_samsung_timers(bytes_arr: List[int]) -> Optional[Dict[str, float]]:
    """
    Decodes the On and Off timers from a 21-byte Samsung Air Conditioner IR payload.
    
    Args:
        bytes_arr (List[int]): An array of 21 integers representing the raw IR bytes.
        
    Returns:
        Optional[Dict[str, float]]: A dictionary containing 'on_hours' and 'off_hours' as floats.
                                    Returns None if the payload length is invalid.
    """
    if len(bytes_arr) < 21:
        return None

    timer_15m_units = bytes_arr[12]

    # 1. Extract Off-Timer
    off_val = ((bytes_arr[10] & 0x0F) << 4) + (bytes_arr[9] >> 4)
    off_hours = 0.0
    if bytes_arr[8] == 0xB2 and timer_15m_units > 0:
        off_hours = timer_15m_units / 4.0
    elif off_val > 0:
        off_hours = (off_val // 8) + (0.5 if off_val % 8 == 3 else 0.0)

    # 2. Extract On-Timer
    on_val = ((bytes_arr[11] & 0x0F) << 4) + (bytes_arr[10] >> 4)
    on_hours = 0.0
    if bytes_arr[8] == 0xA2 and timer_15m_units > 0:
        on_hours = timer_15m_units / 4.0
    elif on_val > 0:
        on_hours = (on_val // 8) + (0.5 if on_val % 8 == 3 else 0.0)

    return {
        "on_hours": on_hours,
        "off_hours": off_hours
    }
